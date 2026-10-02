import pandas as pd
from app.config import SITE_LABELS, TRUST
from app.models.schemas import Product
from app.utils.price import fmt_inr

PRIOR_M, PRIOR_C = 3.8, 50  # Bayesian prior mean rating and pseudo-count
W = {"price": 0.45, "discount": 0.20, "rating": 0.15, "delivery": 0.10, "trust": 0.10}


def label(site: str) -> str:
    return SITE_LABELS.get(site, site)

def rank(products: list[Product]) -> tuple[list[Product], dict]:
    if not products:
        return [], {}
    df = pd.DataFrame([{
        "i": i, "site": p.site, "price": p.price, "disc": p.discount_percent or 0.0,
        "rating": p.rating, "rc": p.review_count or 0, "days": p.delivery.estimated_days, "verified": p.verified,
    } for i, p in enumerate(products)])
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["days"] = pd.to_numeric(df["days"], errors="coerce")
    pmin, pmax = df.price.min(), df.price.max()
    df["price_score"] = 100.0 if pmax == pmin else (pmax - df.price) / (pmax - pmin) * 100
    df["discount_score"] = df.disc.clip(0, 70) / 70 * 100
    df["bayes"] = (df.rc * df.rating.fillna(PRIOR_M) + PRIOR_C * PRIOR_M) / (df.rc + PRIOR_C)
    df["rating_score"] = ((df.bayes - 1) / 4 * 100).clip(0, 100)
    df["delivery_score"] = df.days.apply(lambda d: 40.0 if pd.isna(d) else max(0.0, 100 - 12 * float(d)))
    df["trust_score"] = df.site.map(lambda s: TRUST.get(s, 0.7) * 100)
    df["score"] = (W["price"] * df.price_score + W["discount"] * df.discount_score + W["rating"] * df.rating_score
                   + W["delivery"] * df.delivery_score + W["trust"] * df.trust_score)
    df.loc[~df.verified, "score"] *= 0.9
    for _, row in df.iterrows():
        products[int(row.i)].score = round(float(row.score), 1)

    cheapest = products[int(df.loc[df.price.idxmin(), "i"])]
    best = products[int(df.loc[df.score.idxmax(), "i"])]
    fast_df = df.dropna(subset=["days"])
    fastest = products[int(fast_df.loc[fast_df.days.idxmin(), "i"])] if not fast_df.empty else None
    top_rated = products[int(df.loc[df.bayes.idxmax(), "i"])] if df.rating.notna().any() else None

    cheapest.badges.append("CHEAPEST")
    best.badges.append("BEST_DEAL")
    if fastest:
        fastest.badges.append("FASTEST")
    if top_rated:
        top_rated.badges.append("TOP_RATED")

    site_min = df.groupby("site").price.min().sort_values()
    if len(site_min) > 1:
        second_site, second_price = site_min.index[1], site_min.iloc[1]
        explanation = (f"Cheapest on {label(cheapest.site)} at {fmt_inr(cheapest.price)}, "
                       f"{fmt_inr(second_price - cheapest.price)} below {label(second_site)}.")
    else:
        explanation = f"Only {label(cheapest.site)} returned results: lowest is {fmt_inr(cheapest.price)}."
    highest = float(site_min.max())
    saving = highest - cheapest.price
    best_reason = (f"{label(best.site)} scores {best.score:.0f}/100: {fmt_inr(best.price)}"
                   + (f", {best.discount_percent:.0f}% off" if best.discount_percent else "")
                   + (f", {best.rating}★" if best.rating else "")
                   + (f", delivery in {best.delivery.estimated_days} day(s)" if best.delivery.estimated_days is not None else "")
                   + ".")
    products.sort(key=lambda p: p.score, reverse=True)
    summary = {
        "cheapest": {"id": cheapest.id, "site": cheapest.site, "price": cheapest.price},
        "best_deal": {"id": best.id, "site": best.site, "price": best.price, "score": best.score, "reason": best_reason},
        "fastest_delivery": {"id": fastest.id, "site": fastest.site, "price": fastest.price,
                             "days": fastest.delivery.estimated_days} if fastest else None,
        "highest_rated": {"id": top_rated.id, "site": top_rated.site, "rating": top_rated.rating} if top_rated else None,
        "savings_vs_highest": {"inr": round(saving, 2), "percent": round(saving / highest * 100, 1) if highest else 0.0},
        "explanation": explanation,
    }
    return products, summary