
import json
from pathlib import Path
from typing import List, Dict, Any

def load_kb() -> List[Dict[str, Any]]:
    kb_path = Path(__file__).parent / "kb.json"
    if not kb_path.exists():
        return []
    return json.loads(kb_path.read_text(encoding="utf-8"))
