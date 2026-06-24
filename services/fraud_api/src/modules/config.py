# from pydantic import BaseModel, Field
#
# class ApiConfig(BaseModel):
#     prediction_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
#     max_latency_ms:       float = Field(default=500.0, gt=0.0)
#
# api_config = ApiConfig()