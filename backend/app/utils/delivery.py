import re
from datetime import date, timedelta

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
_MON = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"


def _future(d: int, m: int, today: date) -> date | None:
    try:
        cand = date(today.year, m, d)
    except ValueError:
        return None
    if cand < today - timedelta(days=1):
        cand = date(today.year + 1, m, d)
    return cand
def parse_delivery(text: str | None, today: date | None = None) -> dict:
    out = {"text": text, "estimated_date": None, "estimated_days": None, "free": False}
    if not text:
        return out
    today = today or date.today()
    t = text.lower()
    out["free"] = "free" in t
    target: date | None = None
    if re.search(r"\btoday\b", t):
        target = today
    elif re.search(r"\btomorrow\b", t):
        target = today + timedelta(days=1)
    else:
        m = re.search(rf"(\d{{1,2}})(?:st|nd|rd|th)?\s*({_MON})[a-z]*", t)
        if m:
            target = _future(int(m.group(1)), MONTHS[m.group(2)], today)
        else:
            m = re.search(rf"({_MON})[a-z]*\s*(\d{{1,2}})", t)
            if m:
                target = _future(int(m.group(2)), MONTHS[m.group(1)], today)
            else:
                m = re.search(r"(\d+)\s*(?:-\s*(\d+)\s*)?(?:business\s*|working\s*)?days?", t)
                if m:
                    target = today + timedelta(days=int(m.group(2) or m.group(1)))
    if target:
        out["estimated_date"] = target.isoformat()
        out["estimated_days"] = max(0, (target - today).days)
    return out