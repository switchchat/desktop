"""Schema loader for Notion tool JSON schemas."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List


def get_schemas() -> List[Dict[str, Any]]:
    """Load and return the tool schemas from the packaged JSON file.

    Falls back to an empty list if the JSON file is not present.
    """
    base = os.path.dirname(__file__)
    path = os.path.join(base, "schemas.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []
