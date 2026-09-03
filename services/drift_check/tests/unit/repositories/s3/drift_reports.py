from services.drift_check.src.repositories.s3.drift_reports import upload_drift_report

def test_upload_drift_report_calls_ensure_bucket(mocker):
    mock_ensure = mocker.patch("services.drift_check.src.repositories.s3.drift_reports.ensure_bucket")
    mocker.patch("services.drift_check.src.repositories.s3.drift_reports.s3_client")
    upload_drift_report(b"<html/>", b"{}")
    mock_ensure.assert_called_once()

def test_upload_drift_report_uploads_html(mocker):
    mocker.patch("services.drift_check.src.repositories.s3.drift_reports.ensure_bucket")
    mock_client = mocker.patch("services.drift_check.src.repositories.s3.drift_reports.s3_client")
    upload_drift_report(b"<html/>", b"{}")
    mock_client.upload_fileobj.assert_called_once()
    html_key = mock_client.upload_fileobj.call_args[1]["Key"]
    assert html_key.endswith("drift_report.html")

def test_upload_drift_report_puts_json(mocker):
    mocker.patch("services.drift_check.src.repositories.s3.drift_reports.ensure_bucket")
    mock_client = mocker.patch("services.drift_check.src.repositories.s3.drift_reports.s3_client")
    upload_drift_report(b"<html/>", b"{}")
    mock_client.put_object.assert_called_once()
    json_key = mock_client.put_object.call_args[1]["Key"]
    assert json_key.endswith("drift_report.json")

def test_upload_drift_report_uses_date_partition(mocker):
    mocker.patch("services.drift_check.src.repositories.s3.drift_reports.ensure_bucket")
    mock_client = mocker.patch("services.drift_check.src.repositories.s3.drift_reports.s3_client")
    upload_drift_report(b"<html/>", b"{}")
    key = mock_client.upload_fileobj.call_args[1]["Key"]
    assert "year=" in key and "month=" in key and "day=" in key
