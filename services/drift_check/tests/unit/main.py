import json

import pytest
from pytest_mock import MockerFixture

from services.drift_check.src.modules.configs.airflow.xcom import DriftCheckXComKeys
from services.drift_check.src.modules.configs.evidently import EvidentlyConfig
from services.shared.src.modules.configs.airflow import AirflowConfig

@pytest.mark.usefixtures("fs")
def test_main(mocker: MockerFixture):
    mocker.patch(
        "services.drift_check.src.main.drift_check",
        return_value=(
            True,
            {
                EvidentlyConfig.data_drift_key: {},
                EvidentlyConfig.concept_drift_key: {}
            }
        ),
    )

    from services.drift_check.src.main import main
    main()

    with open(AirflowConfig.xcom_file_path) as file:
        result = json.loads(file.read())

    assert DriftCheckXComKeys.drift_detected in result
    assert DriftCheckXComKeys.drift_summary in result

    drift_detected = result[DriftCheckXComKeys.drift_detected]
    assert isinstance(drift_detected, bool)

    drift_summary = result[DriftCheckXComKeys.drift_summary]
    assert isinstance(drift_summary, dict)
    assert EvidentlyConfig.data_drift_key in drift_summary
    assert EvidentlyConfig.concept_drift_key in drift_summary