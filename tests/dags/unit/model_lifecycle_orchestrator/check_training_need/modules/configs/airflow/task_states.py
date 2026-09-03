from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_states import CurrentModelDeploymentWorkflowForTrainingStates

def test_states_is_str_enum():
    from enum import StrEnum
    assert issubclass(CurrentModelDeploymentWorkflowForTrainingStates, StrEnum)

def test_train_the_challenger():
    assert CurrentModelDeploymentWorkflowForTrainingStates.train_the_challenger == "train_the_challenger"

def test_train_and_replace_the_challenger():
    assert CurrentModelDeploymentWorkflowForTrainingStates.train_and_replace_the_challenger == "train_and_replace_the_challenger"

def test_train_the_challenger_substitute():
    assert CurrentModelDeploymentWorkflowForTrainingStates.train_the_challenger_substitute == "train_the_challenger_substitute"

def test_train_and_replace_the_challenger_substitute():
    assert CurrentModelDeploymentWorkflowForTrainingStates.train_and_replace_the_challenger_substitute == "train_and_replace_the_challenger_substitute"
