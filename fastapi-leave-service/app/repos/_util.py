from datetime import datetime, timezone
from typing import Optional

def _epoch_to_dt(ts: Optional[int]) -> Optional[datetime]:
    """Convierte epoch (int) a datetime con tz=UTC o devuelve None."""
    return datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None