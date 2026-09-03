from services.shared.src.repositories.s3.s3 import s3_client

def test_s3_client_is_not_none():
    assert s3_client is not None

def test_s3_client_is_boto3_client():
    # boto3 clients don't have a public base class, check for common methods
    assert hasattr(s3_client, "upload_fileobj")
    assert hasattr(s3_client, "head_bucket")
    assert hasattr(s3_client, "create_bucket")
    assert hasattr(s3_client, "put_object")
