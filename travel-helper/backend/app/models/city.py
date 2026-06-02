"""城市数据模型."""

import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

CITIES_FILE = Path(__file__).parent.parent.parent / "data" / "cities.json"


class City(BaseModel):
    """城市实体."""

    name: str
    pinyin: str
    province: str
    code: str


def load_cities() -> list[City]:
    """从 JSON 文件加载城市列表."""
    if not CITIES_FILE.exists():
        return []
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [City(**item) for item in data]
