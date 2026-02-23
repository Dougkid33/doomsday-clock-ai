# src/infra/official_clock.py
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Optional

import requests
from bs4 import BeautifulSoup

BULLETIN_CLOCK_URL = "https://thebulletin.org/doomsday-clock/"

@dataclass(frozen=True)
class OfficialClock:
    seconds_to_midnight: int
    as_of: Optional[date]
    source_url: str

def fetch_official_clock(timeout: int = 15) -> OfficialClock:
    """
    Lê a página oficial do Bulletin e extrai o valor atual em segundos.
    Exemplo de texto na página:
      "On January 27, 2026, the Doomsday Clock was set at 85 seconds to midnight"
    """
    r = requests.get(BULLETIN_CLOCK_URL, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    # seconds
    m = re.search(r"set at\s+(\d+)\s+seconds?\s+to midnight", text, flags=re.IGNORECASE)
    if not m:
        # fallback: tenta outra variação
        m = re.search(r"now stands at\s+(\d+)\s+seconds?\s+to midnight", text, flags=re.IGNORECASE)

    if not m:
        raise ValueError("Não consegui extrair 'seconds to midnight' do Bulletin.")

    seconds = int(m.group(1))

    # date
    dm = re.search(r"On\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", text)
    as_of = None
    if dm:
        month_name, day_str, year_str = dm.group(1), dm.group(2), dm.group(3)
        # parse simples (inglês)
        months = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12,
        }
        if month_name in months:
            as_of = date(int(year_str), months[month_name], int(day_str))

    return OfficialClock(seconds_to_midnight=seconds, as_of=as_of, source_url=BULLETIN_CLOCK_URL)