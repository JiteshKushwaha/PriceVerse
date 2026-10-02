"""PriceVerse: Streamlit edition.
Mode 1 (default, works on Streamlit Cloud with no backend): built-in demo data generator.
Mode 2: set secret/env API_BASE_URL=https://your-backend to call the live FastAPI backend.
"""
import os
import sys
import pathlib
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "app" / "services"))
import demo_data  # noqa: E402  (stdlib-only module from the backend)

LABELS = {"amazon.in": "Amazon", "flipkart.com": "Flipkart", "myntra.com": "Myntra", "croma.com": "Croma",
          "reliancedigital.in": "Reliance Digital", "ajio.com": "AJIO", "snapdeal.com": "Snapdeal", "tatacliq.com": "Tata CLiQ"}
TRUST = {"amazon.in": .95, "flipkart.com": .93, "croma.com": .90, "reliancedigital.in": .88, "tatacliq.com": .86,
         "myntra.com": .90, "ajio.com": .85, "snapdeal.com": .70}


def api_base() -> str:
    try:
        return st.secrets.get("API_BASE_URL", "") or os.getenv("API_BASE_URL", "")
    except Exception:
        return os.getenv("API_BASE_URL", "")


def inr(v: float) -> str:
    s = str(int(round(v)))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return "₹" + s


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Inter:wght@400;700&family=Space+Mono:wght@700&display=swap');
.stApp { background-color:#0B0B12;
  background-image: radial-gradient(rgba(255,46,147,.18) 1.2px, transparent 1.4px); background-size:10px 10px; }
h1, h2, h3 { font-family:'Bangers', cursive !important; letter-spacing:2px; transform:skew(-8deg);
  text-shadow:3px 3px 0 #00E5FF, -3px -3px 0 #FF2E93; }
.card { background:#101428; border:3px solid #000; box-shadow:6px 6px 0 #000; border-radius:6px; padding:14px; margin-bottom:8px; color:#F7F3E8; }
.red { background:#E23636; color:#fff; } .cyan { background:#00E5FF; color:#0B0B12; } .yellow { background:#FFD60A; color:#0B0B12; }
.price { font-family:'Space Mono', monospace; font-size:1.6rem; font-weight:700; }
.demo { background:#7B2FF7; color:#fff; border:3px solid #000; padding:8px 12px; font-weight:700; border-radius:6px; }
.stButton>button, .stLinkButton>a { font-family:'Bangers', cursive !important; font-size:1.2rem !important; letter-spacing:1px;
  background:#E23636 !important; color:#fff !important; border:3px solid #000 !important; box-shadow:3px 3px 0 #000; }
</style>
"""


def demo_search(q: str) -> dict:
    rows = []
    for site, items in demo_data.generate_items(q).items():
        for it in items:
            mrp = it["mrp"]
            rows.append({"site": site, "name": it["name"], "price": it["price"], "mrp": mrp,
                         "discount_percent": round((mrp - it["price"]) / mrp * 100, 1) if mrp > it["price"] else 0,
                         "rating": it["rating"], "review_count": it["review_count"], "delivery": it["delivery_text"],
                         "days": int("".join(c for c in it["delivery_text"] if c.isdigit()) or 5),
                         "free": "FREE" in it["delivery_text"], "url": it["url"], "in_stock": it["in_stock"]})
    return {"demo": True, "rows": rows}


def api_search(base: str, q: str) -> dict:
    r = requests.get(f"{base.rstrip('/')}/api/search", params={"q": q}, timeout=60)
    r.raise_for_status()
    d = r.json()
    rows = [{"site": p["site"], "name": p["name"], "price": p["price"], "mrp": p["mrp"] or p["price"],
             "discount_percent": p["discount_percent"] or 0, "rating": p["rating"], "review_count": p["review_count"] or 0,
             "delivery": p["delivery"]["text"] or "", "days": p["delivery"]["estimated_days"],
             "free": p["delivery"]["free"], "url": p["url"], "in_stock": p["in_stock"]} for p in d["results"]]
    return {"demo": d.get("demo", False), "rows": rows}


def score(df: pd.DataFrame) -> pd.DataFrame:
    pmin, pmax = df.price.min(), df.price.max()
    price_s = 100.0 if pmax == pmin else (pmax - df.price) / (pmax - pmin) * 100
    disc_s = df.discount_percent.clip(0, 70) / 70 * 100
    rc = df.review_count.fillna(0)
    bayes = (rc * df.rating.fillna(3.8) + 50 * 3.8) / (rc + 50)
    rating_s = ((bayes - 1) / 4 * 100).clip(0, 100)
    deliv_s = df.days.fillna(5).apply(lambda d: max(0, 100 - 12 * d))
    trust_s = df.site.map(lambda s: TRUST.get(s, .7) * 100)
    df["score"] = (.45 * price_s + .20 * disc_s + .15 * rating_s + .10 * deliv_s + .10 * trust_s).round(1)
    return df.sort_values("score", ascending=False)


st.set_page_config(page_title="PriceVerse", page_icon="🕸️", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.title("SWING TO THE BEST PRICE!")
st.caption("E-Commerce Price Comparison & Product Recommendation System · Data Engineering Honours: Web Scraping & APIs")

c1, c2 = st.columns([4, 1])
q = c1.text_input("Search a product", value=st.query_params.get("q", "iphone 15"), max_chars=100)
go = c2.button("SWING! 🕸️", use_container_width=True)
st.write("Quick picks: iphone 15 · boat airdopes 141 · nike air max · sony wh-1000xm5 · macbook air m2")

if q and (go or "q" in st.query_params):
    q = q.strip()
    if len(q) < 2:
        st.error("Type at least 2 characters, hero!")
        st.stop()
    st.query_params["q"] = q
    base = api_base()
    with st.spinner("Spidey-sense tingling… crawling the web"):
        try:
            res = api_search(base, q) if base else demo_search(q)
        except Exception as exc:
            st.warning(f"Backend unavailable ({exc}). Using demo data.")
            res = demo_search(q)
    if not res["rows"]:
        st.info("No webs here! Try another product.")
        st.stop()
    if res["demo"]:
        st.markdown('<div class="demo">DEMO DATA: prices are simulated; links open real store searches.</div>', unsafe_allow_html=True)

    df = score(pd.DataFrame(res["rows"]))
    cheapest = df.loc[df.price.idxmin()]
    best = df.iloc[0]
    fastest = df.loc[df.days.fillna(99).idxmin()]
    site_min = df.groupby("site").price.min().sort_values()

    cols = st.columns(3)
    for col, title, tone, row in ((cols[0], "CHEAPEST", "red", cheapest), (cols[1], "BEST DEAL", "cyan", best),
                                  (cols[2], "FASTEST DELIVERY", "yellow", fastest)):
        col.markdown(f'<div class="card {tone}"><b style="font-family:Bangers;font-size:1.5rem">{title}</b><br>'
                     f'{LABELS.get(row.site, row.site)}<div class="price">{inr(row.price)}</div>{row["name"]}</div>',
                     unsafe_allow_html=True)
    if len(site_min) > 1:
        st.info(f"💬 Cheapest on {LABELS[site_min.index[0]]} at {inr(site_min.iloc[0])}, "
                f"{inr(site_min.iloc[1] - site_min.iloc[0])} below {LABELS[site_min.index[1]]}. "
                f"Save {inr(site_min.max() - site_min.min())} vs the priciest store.")

    st.header("COMPARISON TABLE")
    per_site = df.loc[df.groupby("site").price.idxmin()].sort_values("price")
    table = per_site.assign(Store=per_site.site.map(LABELS), Price=per_site.price.map(inr),
                            Discount=per_site.discount_percent.map(lambda x: f"{x}%"))
    st.dataframe(table[["Store", "name", "Price", "Discount", "rating", "delivery", "score", "url"]],
                 column_config={"url": st.column_config.LinkColumn("Go to store", display_text="GO ➜"),
                                "name": "Product", "rating": "Rating", "delivery": "Delivery", "score": "Score"},
                 hide_index=True, use_container_width=True)

    st.header("PRICE INSIGHTS")
    chart = site_min.reset_index().assign(Store=lambda d: d.site.map(LABELS))
    fig = px.bar(chart, x="Store", y="price", color="price", color_continuous_scale=["#00E5FF", "#FF2E93"],
                 labels={"price": "Lowest price (₹)"})
    fig.update_layout(paper_bgcolor="#101428", plot_bgcolor="#101428", font_color="#F7F3E8", coloraxis_showscale=False)
    fig.update_traces(marker_line_color="#000", marker_line_width=2)
    st.plotly_chart(fig, use_container_width=True)

    st.header("ALL DEALS")
    for _, r in df.iterrows():
        a, b = st.columns([5, 1])
        a.markdown(f'<div class="card"><b>{LABELS.get(r.site, r.site)}</b> · score {r.score}<br>{r["name"]}<br>'
                   f'<span class="price">{inr(r.price)}</span> <s>{inr(r.mrp)}</s> · -{r.discount_percent}% · '
                   f'⭐ {r.rating} · 🚚 {r.delivery}</div>', unsafe_allow_html=True)
        b.link_button(f"GO TO {LABELS.get(r.site, r.site).upper()} ➜", r.url, use_container_width=True)

st.markdown("---")
st.caption("Made with ❤ for Data Engineering Honours: Web Scraping & APIs. Prices may change; check on the store's site before buying.")