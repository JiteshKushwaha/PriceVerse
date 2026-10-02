import re
from app.models.schemas import QueryInfo
from app.utils.text import strip_html

NOISE = ["best price", "lowest price", "buy online", "buy", "online", "cheap", "cheapest", "deal", "deals", "in india", "price"]
BRANDS = {
    "iphone": "apple", "ipad": "apple", "macbook": "apple", "airpods": "apple", "apple": "apple",
    "galaxy": "samsung", "samsung": "samsung", "oneplus": "oneplus", "redmi": "xiaomi", "xiaomi": "xiaomi",
    "poco": "xiaomi", "realme": "realme", "vivo": "vivo", "oppo": "oppo", "pixel": "google", "nothing": "nothing",
    "boat": "boat", "airdopes": "boat", "rockerz": "boat", "sony": "sony", "jbl": "jbl", "noise": "noise",
    "nike": "nike", "adidas": "adidas", "puma": "puma", "reebok": "reebok", "skechers": "skechers",
    "levis": "levis", "hp": "hp", "dell": "dell", "lenovo": "lenovo", "asus": "asus", "acer": "acer",
    "lg": "lg", "mi": "xiaomi", "motorola": "motorola", "moto": "motorola", "bose": "bose", "fossil": "fossil",
}
COLORS = ["black", "white", "blue", "red", "green", "pink", "yellow", "grey", "gray", "silver", "gold", "purple", "midnight", "starlight"]

def normalize(raw: str) -> QueryInfo:
    text = strip_html(raw).strip()
    clean = re.sub(r"\s+", " ", text.lower())
    for w in NOISE:
        clean = re.sub(rf"\b{re.escape(w)}\b", " ", clean)
    clean = re.sub(r"[^a-z0-9 .\-+]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip() or text.lower().strip()
    tokens = clean.split()
    brand = next((BRANDS[t] for t in tokens if t in BRANDS), None)
    attrs: dict[str, str] = {}
    if m := re.search(r"(\d+)\s*gb\s*ram", clean):
        attrs["ram"] = f"{m.group(1)}gb"
    for m in re.finditer(r"(\d+)\s*(gb|tb)\b(?!\s*ram)", clean):
        attrs["storage"] = f"{m.group(1)}{m.group(2)}"
    if c := next((c for c in COLORS if re.search(rf"\b{c}\b", clean)), None):
        attrs["color"] = c
    if m := re.search(r"\b(?:size|uk|us)\s*(\d{1,2})\b", clean):
        attrs["size"] = m.group(1)
    model_tokens = [t for t in tokens if t not in BRANDS and not re.fullmatch(r"\d+(gb|tb)", t) and t not in COLORS]
    if model_tokens:
        attrs["model"] = " ".join(model_tokens[:3])
    return QueryInfo(raw=raw, clean=clean, brand=brand, tokens=tokens, attributes=attrs)