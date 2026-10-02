"""Download weekly Google Trends interest for "Duolingo" (worldwide).

Run from the repo root:  python src/fetch_trends.py

If Google rate-limits you (HTTP 429), download the CSV by hand instead:
  1. Open https://trends.google.com/trends/explore?date=today%205-y&q=Duolingo
  2. Click the download arrow on "Interest over time"
  3. Save it as data/google_trends.csv
analysis.py reads either format.
"""
import time
from pathlib import Path

from pytrends.request import TrendReq

OUT = Path("data/google_trends.csv")
KEYWORD = "Duolingo"


def main():
    pytrends = TrendReq(hl="en-US", tz=0)
    for attempt in range(3):
        try:
            # A 5-year window returns weekly data, all on one consistent 0-100 scale.
            pytrends.build_payload([KEYWORD], timeframe="today 5-y", geo="")
            df = pytrends.interest_over_time()
            break
        except Exception as e:  # pytrends raises on 429 / timeouts
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(30)
    else:
        raise SystemExit("Google Trends blocked the request. Download the CSV by hand (see top of file).")

    df = df.drop(columns=["isPartial"], errors="ignore").rename(columns={KEYWORD: "interest"})
    df.index.name = "date"
    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT)
    print(f"Saved {len(df)} weekly rows to {OUT} ({df.index.min().date()} to {df.index.max().date()})")


if __name__ == "__main__":
    main()
