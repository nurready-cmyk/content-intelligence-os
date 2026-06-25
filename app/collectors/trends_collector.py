"""
Google Trends collector — tracks rising topics in business categories.
"""

from pytrends.request import TrendReq


BUSINESS_KEYWORDS = [
    "entrepreneurship",
    "business strategy",
    "unit economics",
    "franchise",
    "leadership",
    "negotiation",
    "artificial intelligence business",
    "business model",
    "passive income",
    "startup",
]


def get_trending_topics(geo: str = "US", timeframe: str = "now 7-d") -> list[dict]:
    pytrends = TrendReq(hl="en-US", tz=180)

    results = []
    for i in range(0, len(BUSINESS_KEYWORDS), 5):
        batch = BUSINESS_KEYWORDS[i:i+5]
        try:
            pytrends.build_payload(batch, geo=geo, timeframe=timeframe)
            interest = pytrends.interest_over_time()
            if interest.empty:
                continue
            for kw in batch:
                if kw in interest.columns:
                    avg = interest[kw].mean()
                    results.append({"keyword": kw, "interest": round(avg, 1), "geo": geo})
        except Exception:
            continue

    return sorted(results, key=lambda x: x["interest"], reverse=True)


def get_related_queries(keyword: str, geo: str = "US") -> dict:
    pytrends = TrendReq(hl="en-US", tz=180)
    pytrends.build_payload([keyword], geo=geo, timeframe="now 7-d")
    related = pytrends.related_queries()
    return related.get(keyword, {})
