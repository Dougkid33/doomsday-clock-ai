from datetime import datetime, timezone
from typing import List
import feedparser

from domain.scoring import infer_category
from domain.models import NewsItem

RSS_SOURCES = [
    ("Reuters", "https://www.reuters.com/rssFeed/topNews"),
    ("BBC", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("The Guardian", "https://www.theguardian.com/world/rss"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),

    # --- AMÉRICAS ---
    ("NYT_World", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("G1_Mundo", "https://g1.globo.com/dynamo/mundo/rss2.xml"),

    # --- EUROPA/RUSSIA/UCRÂNIA ---
    ("BBC_World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("TASS_Russia", "https://tass.com/rss/v2.xml"),
    ("KyivIndependent", "https://kyivindependent.com/rss/"),

    # --- ORIENTE MÉDIO ---
    ("Jerusalem_Post", "https://www.jpost.com/rss/rssfeedsheadlines.aspx"),
    ("AlJazeera_English", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Tehran_Times", "https://www.tehrantimes.com/rss"),

    # --- ÁSIA ---
    ("Global_Times_China", "https://www.globaltimes.cn/rss/index.xml"),
    ("Taipei_Times", "https://www.taipeitimes.com/xml/index.xml"),
]


def _parse_dt(entry) -> datetime:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def collect_news(limit_per_source: int = 20) -> List[NewsItem]:
    items: List[NewsItem] = []

    for source, url in RSS_SOURCES:
        feed = feedparser.parse(url)

        for e in feed.entries[:limit_per_source]:
            title = getattr(e, "title", "")[:500]
            summary = getattr(e, "summary", "")[:2000]
            link = getattr(e, "link", "")

            # 🔥 AJUSTE 4.4: inferir categoria por notícia
            text = f"{title}\n{summary}"
            cat = infer_category(text)

            items.append(
                NewsItem(
                    source=source,
                    title=title,
                    summary=summary,
                    url=link,
                    published_at=_parse_dt(e),
                    category=cat,  # ✅ salva categoria
                )
            )

    # remove duplicados por URL
    seen = set()
    unique: List[NewsItem] = []

    for it in items:
        if it.url and it.url not in seen:
            seen.add(it.url)
            unique.append(it)

    return unique