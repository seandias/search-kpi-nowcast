# Can Google searches predict company KPIs?

Companies report operating metrics (users, bookings) once a quarter, weeks after the quarter ends. Google search interest is free and updates every week. This project tests, company by company, whether search data could have told an investor where a KPI was heading **before** the earnings release, and records a prediction for each company's next quarter ahead of time.

## Results so far

| Company | KPI | Quarters tested | Search-change model vs benchmark | Closer than benchmark | Verdict | Takeaway |
|---|---|---|---|---|---|---|
| [Airbnb](companies/airbnb/README.md) | Nights booked | 14 | 9% worse | 6 of 14 | No | The earlier edge rested on one quarter (Q1 2025), and the Q3 2026 miss erased it. Q3 2026 live test: called about 142M nights, actual 155.0M; the benchmark (147.4M) was closer. |
| [Duolingo](companies/duolingo/README.md) | Daily active users | 11 | 4% better | 7 of 11 | Yes, consistently | Small edge in most quarters, but it shrank from 11% to 4% after Q3 2026 and is about even without its best quarter. Q3 2026 live test: called about 62M DAUs, actual 64.9M; the benchmark (62.1M) was closer. |

**The honest summary: search has not shown a useful edge for either company, and it failed its first live test.** Both Q3 2026 predictions were recorded in October, before the releases. Search interest was down about 12% YoY for both companies, so the search-change model forecast a slowdown for both. Instead both KPIs accelerated (Airbnb nights to 16% growth, Duolingo DAUs to 29%), and the naive benchmark (same growth as last quarter) was closer both times. Adding that quarter flipped Airbnb from "only on average" to "no" and cut Duolingo's edge from 11% to 4%.

One possible reason, not a proven one: if more people now get answers from AI assistants instead of Google, search interest can fall without any drop in real demand, which would weaken this signal for every company. It is also a single quarter. Earlier versions of this project showed the same fragility from the other direction (an apparent travel-vs-habit-app contrast that more data reversed), so any one result here should be read with that in mind. `outputs/summary.md` holds the full comparison table, regenerated each run.

New here? The [Duolingo walkthrough notebook](walkthrough_duolingo.ipynb) explains the whole method step by step, with charts. It was written on an earlier version of the data, so its numbers differ from the tables above.

## Method (same for every company)

1. **Compare growth, not levels.** KPIs and searches both trend, so their raw levels correlate whether or not one predicts the other. Year-over-year growth removes the trend and seasonality.
2. **Test out-of-sample.** For each quarter, models are fit only on earlier quarters, then predict that quarter, which is what an analyst could actually have known at the time.
3. **Beat a benchmark.** The bar is a naive forecast that assumes KPI growth stays the same as last quarter. A signal that can't beat this isn't useful.
4. **Check consistency, not just the average.** A model can beat the benchmark on average thanks to one lucky quarter. Each company's results also report how many quarters the search model was closer than the benchmark, and its edge with the single best quarter removed. The verdict is "Yes, consistently" only if it wins on average, in most quarters, and without its best quarter.
5. **Two models:**
   - *Search-change model:* last quarter's KPI growth, adjusted by how much search growth moved since then. Asks whether a turn in searches signals a turn in the KPI.
   - *Search-level model:* KPI growth regressed directly on search growth.

## Repo layout

```
companies/<name>/
    config.json         company name, ticker, KPI label, Google search term, SEC cik, KPI pattern
    kpi.csv             quarterly KPI scraped from SEC filings by scrape_kpi.py, with the filing link and matched text per row
    google_trends.csv   monthly search interest since 2004 (created by fetch_trends.py)
    README.md           write-up of that company's results
outputs/<name>/         results.md and charts per company
outputs/summary.md      comparison across companies
src/scrape_kpi.py       scrapes quarterly KPIs from SEC earnings filings (8-K, Item 2.02)
src/fetch_trends.py     downloads Google Trends data
src/analysis.py         runs the tests, charts and nowcast
```

## Run it

```bash
pip install -r requirements.txt
python src/scrape_kpi.py airbnb      # one company at a time; repeat for duolingo
python src/fetch_trends.py --all     # or one company: python src/fetch_trends.py airbnb
python src/analysis.py --all         # or one company: python src/analysis.py airbnb
```

If Google rate-limits the download, save the CSV by hand from trends.google.com (steps at the top of `src/fetch_trends.py`).

## Adding a company

1. Create `companies/<name>/config.json` (copy an existing one and change the fields).
2. Add the company's SEC `cik` to its config, then run `python src/scrape_kpi.py <name> --inspect <word>` to see how its filings word the KPI.
3. Write a `kpi_pattern` in the config (group 1 = current quarter, or 3 groups = two values plus the YoY %), then run `python src/scrape_kpi.py <name>` to build `kpi.csv` automatically.

Good candidates have a consumer-facing KPI that people plausibly search for, and a reason the signal might behave differently from companies already covered.

## Limitations

- **Small samples.** Each company has 11 to 14 tested quarters. Treat results as directional, not as a trading model.
- **Results are sensitive to the data.** Switching from 5 years of weekly search data to the full monthly history changed Duolingo's verdict. Any single result here should be read with that in mind.
- **Searches are not customers.** Search interest mostly reflects discovery and buzz, not repeat usage.
- **Google Trends is relative and sampled.** Values are scaled 0 to 100 within each download and can shift slightly between downloads. Google also changed how it collects Trends data from 1 January 2022, which may affect growth rates across that date.
- **Worldwide search mixes markets.** Region-specific search terms (the `geo` field in `config.json`) are a natural next step.
