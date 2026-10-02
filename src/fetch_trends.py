"""Download weekly Google Trends interest for one company (or all of them).

Run from the repo root:
    python src/fetch_trends.py duolingo
    python src/fetch_trends.py --all

The search term and region come from companies/<name>/config.json.

If Google rate-limits you (HTTP 429), download the CSV by hand instead:
  1. Open https://trends.google.com/trends/explore?date=today%205-y&q=<search term>
  2. Click the download arrow on "Interest over time"
  3. Save it as companies/<name>/google_trends.csv
analysis.py reads either format.
"""
import json
import sys
import time
from pathlib import Path

from pytrends.request import TrendReq

COMPANIES = Path("companies")


def fetch(slug):
    cfg = json.loads((COMPANIES / slug / "config.json").read_text())
    term = cfg["search_term"]
    pytrends = TrendReq(hl="en-US", tz=0)
    for attempt in range(3):
        try:
            # A 5-year window returns weekly data, all on one consistent 0-100 scale.
            pytrends.build_payload([term], timeframe="today 5-y", geo=cfg.get("geo", ""))
            df = pytrends.interest_over_time()
            break
        except Exception as e:  # pytrends raises on 429 / timeouts
            print(f"[{slug}] attempt {attempt + 1} failed: {e}")
            time.sleep(30)
    else:
        raise SystemExit(f"[{slug}] Google Trends blocked the request. Download the CSV by hand (see top of file).")

    df = df.drop(columns=["isPartial"], errors="ignore").rename(columns={term: "interest"})
    df.index.name = "date"
    out = COMPANIES / slug / "google_trends.csv"
    df.to_csv(out)
    print(f"[{slug}] saved {len(df)} weekly rows to {out} ({df.index.min().date()} to {df.index.max().date()})")


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit("Usage: python src/fetch_trends.py <company> | --all")
    slugs = sorted(p.name for p in COMPANIES.iterdir() if (p / "config.json").exists()) if args == ["--all"] else args
    for i, slug in enumerate(slugs):
        if i:
            time.sleep(10)  # be gentle with Google between companies
        fetch(slug)


if __name__ == "__main__":
    main()
