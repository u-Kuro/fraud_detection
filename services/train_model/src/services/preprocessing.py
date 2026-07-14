from imblearn.over_sampling import SMOTE
from pandas import DataFrame
from sklearn.model_selection import train_test_split, StratifiedKFold

from services.shared.modules.schemas import FraudClassificationLabel
from services.train_model.src.modules.configs import training_config
from services.train_model.src.modules.schemas.preprocessing import PreprocessOutputs

def preprocess(dataset: DataFrame) -> PreprocessOutputs:
    label_key = FraudClassificationLabel.model_field_key()
    x = dataset.drop(label_key, axis=1).values
    y = dataset[label_key].values

    X_train, X_test, y_train, y_test = train_test_split(
        x, y,
        test_size=training_config.TEST_SIZE,
        random_state=training_config.RANDOM_STATE,
        stratify=y
    )

    original_y_train_positive_scale = (y_train == 0).sum() / (y_train == 1).sum()

    smote = SMOTE(random_state=training_config.RANDOM_STATE)
    X_train, y_train = smote.fit_resample(X_train, y_train)

    cross_validation = StratifiedKFold(
        n_splits=int(1 / training_config.CV_VAL_SIZE),
        shuffle=True,
        random_state=training_config.RANDOM_STATE
    )

    return PreprocessOutputs(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        original_y_train_positive_scale=original_y_train_positive_scale,
        cross_validation=cross_validation
    )