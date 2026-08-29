from imblearn.over_sampling import SMOTE
from pandas import DataFrame
from sklearn.model_selection import train_test_split, StratifiedKFold

from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferences
from services.train_model.src.modules.configs.training import TrainingConfig
from services.train_model.src.modules.schemas.preprocessing import PreprocessOutputs

def preprocess(dataset: DataFrame) -> PreprocessOutputs:
    x = dataset.drop(TransactionInferences.is_fraud.key, axis=1).values
    y = dataset[TransactionInferences.is_fraud.key].values

    X_train, X_test, y_train, y_test = train_test_split(
        x, y,
        test_size=TrainingConfig.test_size,
        random_state=TrainingConfig.random_state,
        stratify=y
    )

    original_y_train_positive_scale = (y_train == 0).sum() / (y_train == 1).sum()

    smote = SMOTE(random_state=TrainingConfig.random_state)
    X_train, y_train = smote.fit_resample(X_train, y_train)

    cross_validation = StratifiedKFold(
        n_splits=int(1 / TrainingConfig.cv_val_size()),
        shuffle=True,
        random_state=TrainingConfig.random_state
    )

    return PreprocessOutputs(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        original_y_train_positive_scale=original_y_train_positive_scale,
        cross_validation=cross_validation
    )