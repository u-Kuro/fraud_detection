from enum import StrEnum

class TrainModelXComKeys(StrEnum):
    model_trained_at_datetime = "model_trained_at_datetime"
    model_mlflow_run_id = "model_mlflow_run_id"
    model_name = "model_name"
    model_version = "model_version"
    model_dataset_min_datetime = "model_dataset_min_datetime"
    model_dataset_max_datetime = "model_dataset_max_datetime"
    model_f1_score = "model_f1_score"
    model_pr_auc = "model_pr_auc"
    model_recall = "model_recall"
    model_precision = "model_precision"