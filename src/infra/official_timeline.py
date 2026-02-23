# src/infra/official_timeline.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd
import requests

WIKI_URL = "https://en.wikipedia.org/wiki/Doomsday_Clock"

@dataclass(frozen=True)
class TimelinePoint:
    year: int
    seconds_to_midnight: int

def _to_seconds(value) -> int:
    """
    value pode vir como:
    - int (minutos)
    - string "100 seconds"
    - string "2" (minutos)
    """
    s = str(value).strip().lower()
    # seconds explicit
    if "second" in s:
        n = int("".join(ch for ch in s if ch.isdigit()))
        return n
    # minutes
    n = int(float(s))
    return n * 60

def fetch_timeline_from_wikipedia() -> List[TimelinePoint]:
    html = requests.get(WIKI_URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
    tables = pd.read_html(html)

    # A tabela "Timeline of the Doomsday Clock" normalmente é a maior/mais relevante com coluna Year.
    # Vamos achar a primeira que contenha "Year" e alguma coluna que represente "midnight" (min/seconds).
    target = None
    for t in tables:
        cols = [c.lower() for c in t.columns.astype(str)]
        if "year" in cols and any("midnight" in c for c in cols):
            target = t
            break
        # alguns dumps usam "minutes to midnight" etc.
        if "year" in cols and any("clock" in c for c in cols):
            target = t
            break

    if target is None:
        raise ValueError("Não encontrei a tabela de timeline no Wikipedia.")

    # Tenta localizar colunas
    col_year = [c for c in target.columns if str(c).lower() == "year"][0]
    # coluna mais provável
    col_midnight = None
    for c in target.columns:
        if "midnight" in str(c).lower():
            col_midnight = c
            break
    if col_midnight is None:
        # fallback
        col_midnight = target.columns[1]

    points: List[TimelinePoint] = []
    for _, row in target.iterrows():
        try:
            year = int(row[col_year])
        except Exception:
            continue

        try:
            sec = _to_seconds(row[col_midnight])
        except Exception:
            continue

        points.append(TimelinePoint(year=year, seconds_to_midnight=sec))

    # remove duplicados e ordena
    uniq = {}
    for p in points:
        uniq[p.year] = p.seconds_to_midnight

    return [TimelinePoint(y, uniq[y]) for y in sorted(uniq.keys())]