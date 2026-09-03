from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_ids import NoActionTaskIDs, DispatchTrainingApprovalTaskIDs, SetupTrainingApprovalTaskIDs

def test_no_action_task_ids_is_str_enum():
    from enum import StrEnum
    assert issubclass(NoActionTaskIDs, StrEnum)

def test_dispatch_training_approval_task_ids_is_str_enum():
    from enum import StrEnum
    assert issubclass(DispatchTrainingApprovalTaskIDs, StrEnum)

def test_setup_training_approval_task_ids_is_str_enum():
    from enum import StrEnum
    assert issubclass(SetupTrainingApprovalTaskIDs, StrEnum)

def test_no_action_task_ids_no_drift():
    assert "no_drift" in NoActionTaskIDs.no_drift

def test_dispatch_training_approval_task_ids_cold_start():
    assert "cold_start" in DispatchTrainingApprovalTaskIDs.cold_start

def test_setup_training_approval_task_ids_post():
    assert "post" in SetupTrainingApprovalTaskIDs.post