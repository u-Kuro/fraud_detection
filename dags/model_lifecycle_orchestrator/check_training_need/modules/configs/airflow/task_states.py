from enum import StrEnum

class CurrentModelDeploymentWorkflowForTrainingStates(StrEnum):
    train_the_challenger = "train_the_challenger"
    train_and_replace_the_challenger = "train_and_replace_the_challenger"
    train_the_challenger_substitute = "train_the_challenger_substitute"
    train_and_replace_the_challenger_substitute = "train_and_replace_the_challenger_substitute"