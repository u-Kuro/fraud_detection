import asyncio

from services.drift_monitor.src.controllers.slack import (
    post_cold_start_training_approval,
    post_training_approval,
    update_training_approval,
)
from services.drift_monitor.src.repositories.postgres.model_deployments import (
    has_any_active_model,
)
from services.drift_monitor.src.repositories.postgres.model_deployment_workflows import (
    get_current_model_deployment_workflow, has_no_ongoing_model_deployment_workflow
)
from services.drift_monitor.src.services.evidently import check_for_drift
from shared.modules.logging import logger
from shared.modules.schemas import ModelDeploymentWorkflowState

async def main() -> None:
    # Any active model corresponds to an existing dataset reference,
    # allowing calculation for drift
    if has_any_active_model():
        drift_detected, drift_summary = check_for_drift()

        if drift_detected:
            current_model_deployment_workflow = get_current_model_deployment_workflow()

            if current_model_deployment_workflow is None:
                await post_training_approval(drift_summary)
                logger.info("Posted new workflow approval for training.")
            elif current_model_deployment_workflow.state == ModelDeploymentWorkflowState.train_pending:
                await update_training_approval(drift_summary, current_model_deployment_workflow)
                logger.info("Updated workflow approval for training for the new drift.")
        else:
            logger.info("No drift found.")

    elif has_no_ongoing_model_deployment_workflow():
        await post_cold_start_training_approval()
        logger.warning("Cold-start: no model deployed. Slack notice was posted.")

    else:
        logger.info("Cold-start was already executed.")

if __name__ == "__main__":
    asyncio.run(main())