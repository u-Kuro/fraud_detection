from dags.shared.repositories.s3.bucket import ensure_bucket

def test_ensure_bucket_does_not_create_if_exists(mocker):
    mock_client = mocker.patch("services.shared.repositories.s3.bucket.s3_client")
    mock_client.head_bucket.return_value = {}

    ensure_bucket("existing-bucket")

    mock_client.head_bucket.assert_called_once_with(Bucket="existing-bucket")
    mock_client.create_bucket.assert_not_called()

def test_ensure_bucket_creates_if_not_exists(mocker):
    mock_client = mocker.patch("services.shared.repositories.s3.bucket.s3_client")
    mock_client.head_bucket.side_effect = Exception("NoSuchBucket")
    mock_client.create_bucket.return_value = {}

    ensure_bucket("new-bucket")

    mock_client.create_bucket.assert_called_once_with(Bucket="new-bucket")

def test_ensure_bucket_passes_bucket_name(mocker):
    mock_client = mocker.patch("services.shared.repositories.s3.bucket.s3_client")
    mock_client.head_bucket.return_value = {}

    ensure_bucket("my-specific-bucket")

    mock_client.head_bucket.assert_called_once_with(Bucket="my-specific-bucket")
