# from datetime import datetime, timezone
# from typing import Optional
# from pydantic import BaseModel, ConfigDict, Field, field_validator
#
# class FraudClassifierFeatures(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     transaction_timestamp: datetime = Field(
#         ..., strict=False, description="Transaction timestamp in UTC"
#     )
#
#     @field_validator("transaction_timestamp")
#     @classmethod
#     def ensure_utc(cls, v: datetime) -> datetime:
#         return v.astimezone(timezone.utc)
#
#     amount: float = Field(..., description="Transaction amount in USD")
#     v1: float = Field(..., description="PCA feature v1")
#     v2: float = Field(..., description="PCA feature v2")
#     v3: float = Field(..., description="PCA feature v3")
#     v4: float = Field(..., description="PCA feature v4")
#     v5: float = Field(..., description="PCA feature v5")
#     v6: float = Field(..., description="PCA feature v6")
#     v7: float = Field(..., description="PCA feature v7")
#     v8: float = Field(..., description="PCA feature v8")
#     v9: float = Field(..., description="PCA feature v9")
#     v10: float = Field(..., description="PCA feature v10")
#     v11: float = Field(..., description="PCA feature v11")
#     v12: float = Field(..., description="PCA feature v12")
#     v13: float = Field(..., description="PCA feature v13")
#     v14: float = Field(..., description="PCA feature v14")
#     v15: float = Field(..., description="PCA feature v15")
#     v16: float = Field(..., description="PCA feature v16")
#     v17: float = Field(..., description="PCA feature v17")
#     v18: float = Field(..., description="PCA feature v18")
#     v19: float = Field(..., description="PCA feature v19")
#     v20: float = Field(..., description="PCA feature v20")
#     v21: float = Field(..., description="PCA feature v21")
#     v22: float = Field(..., description="PCA feature v22")
#     v23: float = Field(..., description="PCA feature v23")
#     v24: float = Field(..., description="PCA feature v24")
#     v25: float = Field(..., description="PCA feature v25")
#     v26: float = Field(..., description="PCA feature v26")
#     v27: float = Field(..., description="PCA feature v27")
#     v28: float = Field(..., description="PCA feature v28")
#
# class FraudClassifierLabel(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     is_fraud: Optional[bool] = None
#
# class FraudClassifierDataset(FraudClassifierFeatures, FraudClassifierLabel):
#     model_config = ConfigDict(strict=True, extra="forbid")