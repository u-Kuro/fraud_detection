from dags.shared.repositories.s3.s3 import s3_hook

def test_s3_hook_is_not_none():
    assert s3_hook is not None
