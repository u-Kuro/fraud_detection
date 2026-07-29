import numpy as np
from matplotlib import pyplot as plt, ticker
from sklearn.metrics import f1_score, average_precision_score, recall_score, precision_score, roc_auc_score, accuracy_score, ConfusionMatrixDisplay

from services.shared.modules.configs.mlflow import MLFlowConfig
from services.train_model.src.modules.schemas.evaluation import EvaluateModelOutputs, ModelEvaluationMetrics, ModelEvaluationFigures

def evaluate_model(
    model: object,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> EvaluateModelOutputs:
    model_predictions = get_predictions_sklearn(model, X_test)

    return EvaluateModelOutputs(
        metrics=evaluate_model_predictions(
            **model_predictions,
            y_true=y_test
        ),
        metric_figures=visualize_model_predictions(
            **model_predictions,
            y_true=y_test,
            title=MLFlowConfig.MODEL_NAME
        )
    )

def get_predictions_sklearn(
    model: object,
    x: np.ndarray,
    threshold: float = 0.5
) -> dict[str, np.ndarray]:
    y_prob = model.predict_proba(x)[:, 1]
    return {
        "y_pred": (y_prob >= threshold).astype(int),
        "y_prob": y_prob
    }

def evaluate_model_predictions(
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    y_true: np.ndarray
) -> ModelEvaluationMetrics:
    return ModelEvaluationMetrics(
        f1_score=float(f1_score(y_true, y_pred)),
        pr_auc=float(average_precision_score(y_true, y_prob)),
        recall=float(recall_score(y_true, y_pred)),
        precision=float(precision_score(y_true, y_pred)),
        roc_auc=float(roc_auc_score(y_true, y_prob)),
        accuracy=float(accuracy_score(y_true, y_pred)),
    )

def visualize_model_predictions(
    title: str,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    y_true: np.ndarray,
    threshold: float = 0.5,
) -> ModelEvaluationFigures:
    confusion_matrix_figure, confusion_matrix_ax = plt.subplots()
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        display_labels=["Legitimate", "Fraud"],
        normalize="true",
        cmap="Blues",
        values_format=".1%",
        ax=confusion_matrix_ax,
    )
    confusion_matrix_ax.set_title(title)

    probability_scatter_figure, probability_scatter_ax = plt.subplots()
    probability_scatter_ax.scatter(
        y_prob,
        range(len(y_true)),
        c=np.where(y_true == 1, "red", "blue"),
        edgecolors="k",
    )
    probability_scatter_ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
    probability_scatter_ax.axvline(x=threshold, alpha=0.3, color="white", linestyle="--")
    probability_scatter_ax.axvspan(threshold, 1.0, alpha=0.05, color="red")
    probability_scatter_ax.axvspan(0.0, threshold, alpha=0.05, color="blue")
    probability_scatter_ax.set_yticks([])
    probability_scatter_ax.set_ylabel("Transactions")
    probability_scatter_ax.set_xlabel("Fraud Probability Score")
    probability_scatter_ax.set_title(title)

    return ModelEvaluationFigures(
        probability_scatter=probability_scatter_figure,
        confusion_matrix=confusion_matrix_figure,
    )