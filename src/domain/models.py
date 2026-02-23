from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class NewsItem:
    source: str
    title: str
    summary: str
    url: str
    published_at: datetime
    category: str = "Geral"

@dataclass(frozen=True)
class ThreatScore:
    item_url: str
    sentiment: float          # 0..1
    keywords: float           # 0..1
    source_weight: float      # 0..1
    recency: float            # 0..1
    final: float              # 0..1
    label: str                # "Baixo", "Médio", "Alto", "Crítico"