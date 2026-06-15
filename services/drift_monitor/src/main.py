"""
Drift monitor — state machine entrypoint.

State transitions implemented here (see STATES AND TRANSITIONS in spec):
  Idle        → post Slack + create drift_pending row
  drift_pending / drift_approved=False → update Slack (in place) + increment drift_count
  drift_pending / drift_approved=True  → update Slack + submit training Argo Workflow
  train_pending  → supersede: delete MLflow run + submit new training Argo Workflow
  promoting      → resume promotion (handled by training_pipeline)

Human actions (approve/reject) come from a Slack action webhook that calls
the Argo Workflows API or a separate /webhook endpoint in fraud_api.
This script handles the automated (cron) side only.
"""
import asyncio
import sys, json
from datetime import datetime, timezone, timedelta

from services.drift_monitor.src.controllers.slack import post_cold_start_notice_to_slack, update_drift_message, \
    post_drift_message
from services.drift_monitor.src.repositories.postgres.deployed_models import has_any_active_deployed_model
from services.drift_monitor.src.repositories.postgres.pipeline_state import get_pipeline_state, create_drift_pending, \
    update_drift_message_id
from services.drift_monitor.src.repositories.postgres.transaction_inferences import load_current_window
from services.drift_monitor.src.services.evidently import run_drift_report
from services.drift_monitor.src.modules.environment import environment
from services.drift_monitor.src.repositories.s3 import load_reference_parquet, upload_drift_report
from services.shared.logging import logger

async def main() -> None:
    # ── No active model yet: skip drift, notify for first training ──────────
    if not has_any_active_deployed_model():
        state_row = get_pipeline_state()

        if state_row is None:
            # First ever cron run — ask for human approval before training anything.
            # TODO: Add workflow submission on api
            slack_message_id = await post_cold_start_notice_to_slack()
            create_drift_pending(slack_message_id)
            logger.warning("No active model. Cold-start notice posted to Slack; awaiting for approval.")
            sys.exit(0)

        if state_row["state"] == "drift_pending" and state_row["drift_approved"]:
            # Human approved — submit the very first training run
            logger.info("Cold-start approved — submitting first training workflow.")
            submit_training_workflow("cold_start")
            sys.exit(0)

        # drift_approved=False still: waiting on human — nothing to do
        logger.info("Cold-start pending human approval.")
        sys.exit(0)

    # ── Load reference dataset from SeaweedFS ──────────────────────────────
    ref_table = load_reference_parquet()
    if ref_table is None:
        logger.warning("No reference dataset in SeaweedFS. Cannot compute drift. Exiting.")
        sys.exit(0)
    df_reference = ref_table.to_pandas()

    if len(df_reference) < environment.MINIMUM_ROWS:
        logger.info(f"Reference dataset too small ({len(df_reference)} rows). Skipping.")
        sys.exit(0)

    # ── Load current window ────────────────────────────────────────────────
    reference_last_date = datetime.fromtimestamp(df_reference["transaction_timestamp"].max(), timezone.utc)
    chosen_cutoff_date = datetime.now(timezone.utc) - timedelta(days=environment.LOOKBACK_DAYS)
    # Limit cutoff to last date of reference
    current_cutoff_date = min(chosen_cutoff_date, reference_last_date)
    df_current = load_current_window(current_cutoff_date)

    if len(df_current) < environment.MINIMUM_ROWS:
        logger.info(f"Current window too small ({len(df_current)} rows). Skipping.")
        sys.exit(0)

    # ── Run drift report ───────────────────────────────────────────────────
    drift_summary, html_bytes = run_drift_report(df_reference, df_current)
    upload_drift_report(html_bytes, json.dumps(drift_summary).encode())

    data_drift = drift_summary["data_drift"].get("dataset_drift_detected", False)
    concept_drift = drift_summary["concept_drift"].get("concept_drift_detected", False)
    drift_detected = data_drift or concept_drift

    if not drift_detected:
        logger.info("No drift detected.")
        sys.exit(0)

    logger.warning(f"Drift detected — data={data_drift} concept={concept_drift}")

    # ── State machine ──────────────────────────────────────────────────────
    state_row = get_pipeline_state()

    if state_row is None:
        slack_message_id = await post_drift_message(drift_summary)
        create_drift_pending(slack_message_id)
        return

    state = state_row["state"]
    drift_approved = state_row["drift_approved"]
    slack_message_id = state_row["slack_message_id"]

    if state == "drift_pending":
        # TODO: Add workflow submission on api
        # TODO: Delete and post instead of replacing in place?
        slack_message_id = await update_drift_message(drift_summary, slack_message_id)
        update_drift_message_id(slack_message_id)
        if drift_approved:
            logger.info("Drift was previously approved — submitting training.")
            submit_training_workflow("drift_reapproved")
        # else: wait for human to approve/dismiss via Slack buttons

    elif state == "train_pending":
        # TODO: Identify this state. To see if it needs to remove previous message for new drift
        # Candidate supersede: submit a new training workflow.
        # training_pipeline will detect the existing candidate run and delete it first.
        logger.info("Drift during train_pending — superseding candidate.")
        await update_drift_message(drift_summary, slack_message_id)
        submit_training_workflow("supersede")

    elif state == "promoting":
        # TODO: Identify this state. To see if it needs to remove previous message for new drift
        # Promoting is transient; do nothing and let training_pipeline finish.
        logger.info("Drift during promotion — ignoring; promotion in progress.")

if __name__ == "__main__":
    asyncio.run(main())