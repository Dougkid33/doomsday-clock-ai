from typing import Dict, List, Tuple

from  domain.scoring import score_item, risk_to_minutes
from  infra.collectors import collect_news
from  infra.repository import SQLiteRepo

def refresh_pipeline(repo: SQLiteRepo) -> Dict[str, float]:
    items = collect_news(limit_per_source=20)
    repo.upsert_news(items)

    scores = [score_item(it) for it in items]
    repo.upsert_scores(scores)

    global_risk = repo.fetch_global_risk()
    minutes = risk_to_minutes(global_risk)

    return {
        "global_risk": global_risk,
        "minutes_to_midnight": minutes,
        "items_collected": len(items),
        "items_scored": len(scores),
    }