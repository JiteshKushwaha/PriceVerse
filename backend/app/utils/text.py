import re
from rapidfuzz import fuzz

ACCESSORY_WORDS = [
    "case", "cover", "back cover", "charger", "cable", "screen guard", "tempered glass",
    "protector", "skin", "adapter", "strap", "pouch", "stand", "holder", "lens guard",]

def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"(\d+)\s*(gb|tb|mah|w|inch|mm)\b", r"\1\2", s)
    return re.sub(r"[^a-z0-9 ]+", " ", s).strip()

def compact(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())

def tokens(s: str) -> list[str]:
    return norm(s).split()

def similarity(query: str, title: str) -> float:
    return fuzz.token_set_ratio(norm(query), norm(title))

def is_accessory(title: str, query: str) -> bool:
    t, q = title.lower(), query.lower()
    return any(re.search(rf"\b{re.escape(w)}\b", t) and w not in q for w in ACCESSORY_WORDS)

def strip_html(s: str) -> str:
    s = re.sub(r"<script.*?>.*?</script>", " ", s, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", s)