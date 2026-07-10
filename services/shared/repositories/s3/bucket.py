from services.shared.repositories.s3 import s3_client

def ensure_bucket(bucket: str) -> None:
    try: s3_client.head_bucket(Bucket=bucket)
    except: s3_client.create_bucket(Bucket=bucket)