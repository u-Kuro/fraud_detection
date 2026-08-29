from dataclasses import dataclass

@dataclass(frozen=True)
class S3Config:
    S3_MLE_BUCKET: str = "mle"