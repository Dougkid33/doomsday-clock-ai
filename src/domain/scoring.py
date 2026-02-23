from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .models import NewsItem, ThreatScore

_analyzer = SentimentIntensityAnalyzer()

DEFAULT_KEYWORDS: Dict[str, float] = {
    # weights 0..1 (quanto mais “existencial”, maior)
    "nuclear": 1.0,
    "war": 0.9,
    "missile": 0.9,
    "radiation": 0.9,
    "atomic": 0.95,
    "world war": 1.0,
    "outbreak": 0.85,
    "pandemic": 0.9,
    "ai arms race": 0.85,
    "climate tipping point": 0.9,
    "catastrophe": 0.8,
    "collapse": 0.75,
    "genocide": 0.9,
    "terror": 0.7,
}

DEFAULT_SOURCE_WEIGHTS: Dict[str, float] = {
    "NYT": 0.95,
    "BBC": 0.92,
    "Reuters": 0.98,
    "AP": 0.95,
    "Al Jazeera": 0.88,
    "The Guardian": 0.90,
}

CATEGORIES = {
    "Nuclear": ["nuclear", "atomic", "radiation"],
    "Guerra": ["war", "missile", "invasion", "strike"],
    "Clima": ["climate", "tipping point", "wildfire", "flood"],
    "Pandemia": ["pandemic", "outbreak", "virus"],
    "IA": ["ai", "arms race", "autonomous weapons"],
}

def infer_category(text: str) -> str:
    t = text.lower()
    best = ("Geral", 0)
    for cat, keys in CATEGORIES.items():
        hits = sum(1 for k in keys if k in t)
        if hits > best[1]:
            best = (cat, hits)
    return best[0]

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def sentiment_score(text: str) -> float:
    # VADER compound: -1..1 (negativo = pior)
    c = _analyzer.polarity_scores(text)["compound"]
    # mapeia: -1..1 -> 0..1, mas invertendo (negativo = alto risco)
    risk = (1 - (c + 1) / 2)  # c=-1 => 1, c=+1 => 0
    return clamp01(risk)

def keyword_score(text: str, keywords: Dict[str, float]) -> float:
    t = text.lower()
    hits: List[float] = []
    for k, w in keywords.items():
        if k in t:
            hits.append(w)
    if not hits:
        return 0.0
    # saturação suave: média + bônus por múltiplos termos
    avg = sum(hits) / len(hits)
    bonus = min(0.2, 0.04 * (len(hits) - 1))
    return clamp01(avg + bonus)

def source_weight(source: str, weights: Dict[str, float]) -> float:
    # default conservador
    return clamp01(weights.get(source, 0.75))

def recency_score(published_at: datetime) -> float:
    # Quanto mais recente, maior o peso (0..1)
    now = datetime.now(timezone.utc)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    age_hours = (now - published_at).total_seconds() / 3600.0

    # 0h => 1.0
    # 72h => ~0.2
    # >7 dias => ~0.05
    if age_hours <= 24:
        return 1.0
    if age_hours <= 72:
        return 0.6
    if age_hours <= 168:
        return 0.35
    return 0.10

def label_from(score: float) -> str:
    if score < 0.25: return "Baixo"
    if score < 0.50: return "Médio"
    if score < 0.75: return "Alto"
    return "Crítico"

@dataclass(frozen=True)
class ScoringConfig:
    w_sentiment: float = 0.35
    w_keywords: float = 0.40
    w_source: float = 0.15
    w_recency: float = 0.10

def score_item(item: NewsItem,
               cfg: ScoringConfig = ScoringConfig(),
               keywords: Dict[str, float] = DEFAULT_KEYWORDS,
               sources: Dict[str, float] = DEFAULT_SOURCE_WEIGHTS) -> ThreatScore:

    text = f"{item.title}\n{item.summary}"

    s = sentiment_score(text)
    k = keyword_score(text, keywords)
    sw = source_weight(item.source, sources)
    r = recency_score(item.published_at)

    final = clamp01(
        s * cfg.w_sentiment +
        k * cfg.w_keywords +
        sw * cfg.w_source +
        r * cfg.w_recency
    )

    return ThreatScore(
        item_url=item.url,
        sentiment=s,
        keywords=k,
        source_weight=sw,
        recency=r,
        final=final,
        label=label_from(final),
    )

def risk_to_minutes(risk: float) -> float:
    """
    Converte risco 0..1 em minutos 12..1.
    Curva suave e controlável (sem colapsar em 0.1).
    """
    risk = clamp01(risk)

    max_minutes = 12.0
    min_minutes = 1.0

    # curva suavizada:
    # - risco baixo -> perto de 12
    # - risco alto -> desce, mas sem "morrer" em 0.1
    minutes = max_minutes - (risk ** 1.6) * (max_minutes - min_minutes)

    return round(max(min_minutes, minutes), 2)