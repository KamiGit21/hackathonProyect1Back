from typing import Dict
from .models import Unit

store: Dict[str, Unit] = {}

# Seed
root = Unit(id="company-root", name="ARCA LTDA.", parentId=None)
store[root.id] = root