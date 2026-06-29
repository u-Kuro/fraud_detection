"""
Drift monitor — state machine entrypoint.

Runs as a KubernetesPodOperator container (DAG: drift_monitor).

State machine (the DAG sensor handles the human-approval gate):
  No state row  →  post Slack cold-start or drift message, INSERT drift_pending
  drift_pending + no training_approved  →  update existing Slack message in-place (new drift info)
  drift_pending + training_approved     →  training approved, DAG already triggered; nothing to do
  train_pending  →  training in progress or done; exit (drift re-detected during training is skipped)
  promoting      →  promotion in progress; exit

XCom written to /airflow/xcom/return.json:
  {"action": "wait_approval"}  — DAG sensor should wait for training_approved
  {"action": "exit"}           — DAG should stop here
"""
import asyncio, json
from datetime import datetime, timezone, timedelta

from services.drift_monitor.src.controllers.slack import (
    post_cold_start_training_approval,
    post_training_approval,
    update_training_approval,
)
from services.drift_monitor.src.modules.configs import drift_config
from services.drift_monitor.src.repositories.postgres.model_deployments import (
    has_any_active_deployed_model,
)
from services.drift_monitor.src.repositories.postgres.model_deployment_workflows import (
    get_current_model_deployment_workflow,
    create_train_pending_workflow,
    update_training_approval_slack_ts,
)
from services.drift_monitor.src.repositories.postgres.transaction_inferences import (
    load_current_window,
)
from services.drift_monitor.src.repositories.s3.dataset_reference import load_reference_parquet
from services.drift_monitor.src.repositories.s3.drift_reports import upload_drift_report
from services.drift_monitor.src.services.evidently import run_drift_report
from shared.modules.logging import logger

async def main() -> None:
    if not has_any_active_deployed_model():
        current_model_deployment_workflow = get_current_model_deployment_workflow()

        if current_model_deployment_workflow is None:
            await post_cold_start_training_approval()
            logger.warning("Cold-start: no model deployed. Slack notice was posted.")
            return

        state = current_model_deployment_workflow["state"]
        training_approved = current_model_deployment_workflow["training_approved"]

        if state == "train_pending":
            if training_approved:
                # Human already approved in a previous run; the DAG sensor already unblocked.
                # Another cron tick fired before training started — nothing to do.
                logger.info("Cold-start already approved.")
                return
            else:
                # Still waiting on human — nothing to do
                logger.info("Cold-start pending human approval.")
                return

        # Any other state (promoting) with no active model is unusual
        logger.warning(f"No active model with state set to {state}.")
        return

    # ── Load reference dataset ───────────────────────────────────────────────
    reference_table = load_reference_parquet()
    if reference_table is None:
        logger.warning("No reference dataset in S3.")
        return

    df_reference = reference_table.to_pandas()
    # ── Load current window ──────────────────────────────────────────────────
    reference_last_date = datetime.fromtimestamp(
        df_reference["transaction_timestamp"].max(),
        timezone.utc
    )
    chosen_cutoff = datetime.now(timezone.utc) - timedelta(days=drift_config.LOOKBACK_DAYS)
    current_cutoff = min(chosen_cutoff, reference_last_date)
    df_current = load_current_window(current_cutoff)

    if len(df_current) < drift_config.MINIMUM_CURRENT_DATASET_ROWS:
        logger.info(f"Current dataset window is too small ({len(df_current)} rows).")
        return

    # ── Run drift report ─────────────────────────────────────────────────────
    drift_summary, html_bytes = run_drift_report(df_reference, df_current)
    upload_drift_report(html_bytes, json.dumps(drift_summary).encode())

    data_drift = drift_summary["data_drift"].get("dataset_drift_detected", False)
    concept_drift = drift_summary["concept_drift"].get("concept_drift_detected", False)
    drift_detected = data_drift or concept_drift

    # ── (b) No drift ────────────────────────────────────────────────────────
    if drift_detected:
        logger.warning(f"Drift detected — data={data_drift} concept={concept_drift}")

        # ── State machine ────────────────────────────────────────────────────────
        current_model_deployment_workflow = get_current_model_deployment_workflow()

        if current_model_deployment_workflow is None:
            # No existing state — post fresh drift message
            training_approval_slack_ts = await post_training_approval(drift_summary)
            create_train_pending_workflow(training_approval_slack_ts)
            return

        state = current_model_deployment_workflow["state"]
        training_approved = current_model_deployment_workflow["training_approved"]
        training_approval_slack_ts = current_model_deployment_workflow["training_approval_slack_ts"]

        if state == "drift_pending":
            # (d) Drift still pending (not yet approved for training) — update Slack message in place
            new_ts = await update_training_approval(drift_summary, training_approval_slack_ts)
            update_training_approval_slack_ts(new_ts)
            if training_approved:
                # Approved but training not started yet — sensor already unblocked
                logger.info("Training already approved; update posted. Exiting.")
            else:
                logger.info("Drift message updated. Awaiting human approval.")
            return
        else:
            # (c) Training is in progress or promotion underway — do not touch anything
            logger.info(f"Drift detected with state set to {state}.")
            return
    else: logger.info("No drift detected.")

if __name__ == "__main__":
    asyncio.run(main())