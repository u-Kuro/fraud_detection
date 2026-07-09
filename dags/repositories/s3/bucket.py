from dags.repositories.s3 import s3_hook

def ensure_bucket(bucket_name: str) -> None:
    if not s3_hook.check_for_bucket(bucket_name):
        s3_hook.create_bucket(bucket_name=bucket_name)