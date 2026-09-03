from dags.shared.repositories.s3.bucket import ensure_bucket

def test_ensure_bucket_does_not_create_if_exists(mocker):
    mock_hook = mocker.patch("dags.shared.repositories.s3.bucket.s3_hook")
    mock_hook.check_for_bucket.return_value = True
    ensure_bucket("existing-bucket")
    mock_hook.create_bucket.assert_not_called()

def test_ensure_bucket_creates_if_not_exists(mocker):
    mock_hook = mocker.patch("dags.shared.repositories.s3.bucket.s3_hook")
    mock_hook.check_for_bucket.return_value = False
    ensure_bucket("new-bucket")
    mock_hook.create_bucket.assert_called_once_with(bucket_name="new-bucket")

def test_ensure_bucket_passes_correct_name(mocker):
    mock_hook = mocker.patch("dags.shared.repositories.s3.bucket.s3_hook")
    mock_hook.check_for_bucket.return_value = True
    ensure_bucket("my-bucket")
    mock_hook.check_for_bucket.assert_called_once_with("my-bucket")
