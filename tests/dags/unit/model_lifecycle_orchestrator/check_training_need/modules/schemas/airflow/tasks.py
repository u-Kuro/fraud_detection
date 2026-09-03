import pytest
from uuid import uuid4

from pydantic import ValidationError

from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.tasks import ExpiredModelDeploymentWorkflow, ReservedModelDeploymentWorkflow, ExpiredAndReservedModelDeploymentWorkflows, ActiveModelDeployment, ModelDeploymentWorkflowForTraining

def test_active_model_deployment_instantiation():
    obj = ActiveModelDeployment(mlflow_run_id="run-abc")
    assert obj.mlflow_run_id == "run-abc"

def test_active_model_deployment_strict_str():
    with pytest.raises(ValidationError):
        ActiveModelDeployment(mlflow_run_id=123)

def test_model_deployment_workflow_for_training_instantiation():
    obj = ModelDeploymentWorkflowForTraining(
        state="train_the_challenger",
        should_train_for_promotion=True,
    )
    assert obj.state == "train_the_challenger"
    assert obj.should_train_for_promotion is True

def test_model_deployment_workflow_for_training_optional_id():
    obj = ModelDeploymentWorkflowForTraining(
        state="train_the_challenger",
        should_train_for_promotion=False,
    )
    assert obj.id is None

def test_expired_model_deployment_workflow_instantiation():
    obj = ExpiredModelDeploymentWorkflow(
        id=uuid4(),
        model_name="xgboost",
        model_version=3,
        mlflow_run_id="run-abc",
        slack_promotion_approval_message_ts="ts.123",
    )
    assert obj.model_name == "xgboost"
    assert obj.model_version == 3

def test_reserved_model_deployment_workflow_instantiation():
    obj = ReservedModelDeploymentWorkflow(model_name="xgboost", model_version=2)
    assert obj.model_name == "xgboost"
    assert obj.model_version == 2

def test_expired_and_reserved_model_deployment_workflows_instantiation():
    expired = ExpiredModelDeploymentWorkflow(
        id=uuid4(),
        model_name="xgboost",
        model_version=3,
        mlflow_run_id="run-abc",
        slack_promotion_approval_message_ts="ts.111",
    )
    reserved = ReservedModelDeploymentWorkflow(model_name="xgboost", model_version=2)
    combined = ExpiredAndReservedModelDeploymentWorkflows(expired=expired, reserved=reserved)
    assert combined.expired is expired
    assert combined.reserved is reserved
