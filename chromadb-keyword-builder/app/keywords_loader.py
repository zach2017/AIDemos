import json
from pathlib import Path
from typing import List, Dict
from chromadb import HttpClient
from keywords_admin import add_or_update_keywords

def load_keywords(client: HttpClient, collection_name: str, data_path: Path) -> int:
    with data_path.open("r", encoding="utf-8") as f:
        items: List[Dict] = json.load(f)
    return add_or_update_keywords(client, collection_name, items)
