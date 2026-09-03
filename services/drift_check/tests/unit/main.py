def test_main_calls_drift_check_and_xcom_push(mocker):
    mock_drift_check = mocker.patch(
        "services.drift_check.src.main.drift_check",
        return_value=(True, {"data_drift": {}, "concept_drift": {}}),
    )
    mock_xcom_push = mocker.patch("services.drift_check.src.main.xcom_push")
    from services.drift_check.src.main import main
    main()
    mock_drift_check.assert_called_once()
    mock_xcom_push.assert_called_once()

def test_main_passes_drift_detected_to_xcom(mocker):
    mocker.patch(
        "services.drift_check.src.main.drift_check",
        return_value=(False, {"data_drift": {}, "concept_drift": {}}),
    )
    mock_xcom_push = mocker.patch("services.drift_check.src.main.xcom_push")
    from services.drift_check.src.main import main
    main()
    pushed = mock_xcom_push.call_args[0][0]
    assert "drift_detected" in pushed
    assert pushed["drift_detected"] is False

def test_main_module_is_importable():
    import services.drift_check.src.main as m
    assert callable(m.main)
