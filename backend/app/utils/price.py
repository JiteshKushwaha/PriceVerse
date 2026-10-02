import re

_NUM = re.compile(r"(\d[\d,]*(?:\.\d+)?)")


def parse_price(value: object) -> float | None:
    """'₹1,29,999' / 'Rs. 999' / 'from ₹499 - ₹899' -> first positive number as float."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if value > 0 else None
    s = str(value)
    for token in ("\u20b9", "Rs.", "Rs", "INR", "MRP", "From", "from"):
        s = s.replace(token, " ")
    m = _NUM.search(s)
    if not m:
        return None
    try:
        n = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    return n if n > 0 else None


def compute_discount(price: float | None, mrp: float | None) -> tuple[float | None, float | None]:
    if not price or not mrp or mrp <= price:
        return None, None
    amount = round(mrp - price, 2)
    return amount, round(amount / mrp * 100, 1)

def fmt_inr(value: float) -> str:
    """Indian digit grouping: 129999 -> ₹1,29,999"""
    s = str(int(round(value)))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = re.sub(r"(\d)(?=(\d{2})+$)", r"\1,", head)
        s = f"{head},{tail}"
    return f"\u20b9{s}"