from pydantic import BaseModel

class DriftConfig(BaseModel):
    """Fixed drift-detection constants. Not environment-driven."""
    max_selected_rows: int   = 50_000
    drift_threshold:   float = 0.5
    minimum_rows:      int   = 500
    lookback_days:     int   = 7

drift_config = DriftConfig()