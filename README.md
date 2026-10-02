# Can Google searches predict company KPIs?

Companies report operating metrics (users, bookings) once a quarter, weeks after the quarter ends. Google search interest is free and updates every week. This project tests, company by company, whether search data could have told an investor where a KPI was heading **before** the earnings release, and records a prediction for each company's next quarter ahead of time.

## Results so far

| Company | KPI | Quarters tested | Beats naive benchmark? | Takeaway |
|---|---|---|---|---|
| [Duolingo](companies/duolingo/README.md) | Daily active users | 7 | No (search-change model 4% worse) | Searches went flat after 2023 while users nearly tripled, pointing to retention-led growth. Q3 2026 call: about 62M DAUs. |
| Airbnb | Nights and experiences booked | | | _Data in place, results pending._ |

`outputs/summary.md` holds the full comparison table, regenerated each run.

New here? The [Duolingo walkthrough notebook](walkthrough_duolingo.ipynb) explains the whole method step by step, with charts, and renders right in the browser.

## Method (same for every company)

1. **Compare growth, not levels.** KPIs and searches both trend, so their raw levels correlate whether or not one predicts the other. Year-over-year growth removes the trend and seasonality.
2. **Test out-of-sample.** For each quarter, models are fit only on earlier quarters, then predict that quarter, which is what an analyst could actually have known at the time.
3. **Beat a benchmark.** The bar is a naive forecast that assumes KPI growth stays the same as last quarter. A signal that can't beat this isn't useful.
4. **Two models:**
   - *Search-change model:* last quarter's KPI growth, adjusted by how much search growth moved since then. Asks whether a turn in searches signals a turn in the KPI.
   - *Search-level model:* KPI growth regressed directly on search growth.

## Repo layout

```
companies/<name>/
    config.json         company name, ticker, KPI label, Google search term
    kpi.csv             quarterly KPI from the company's own filings, with a source link per row
    google_trends.csv   weekly search interest (created by fetch_trends.py)
    README.md           write-up of that company's results
outputs/<name>/         results.md and charts per company
outputs/summary.md      comparison across companies
src/fetch_trends.py     downloads Google Trends data
src/analysis.py         runs the tests, charts and nowcast
```

## Run it

```bash
pip install -r requirements.txt
python src/fetch_trends.py --all     # or one company: python src/fetch_trends.py airbnb
python src/analysis.py --all         # or one company: python src/analysis.py airbnb
```

If Google rate-limits the download, save the CSV by hand from trends.google.com (steps at the top of `src/fetch_trends.py`).

## Adding a company

1. Create `companies/<name>/config.json` (copy an existing one and change the fields).
2. Create `companies/<name>/kpi.csv` from the company's shareholder letters or 10-Qs, with a source link on every row. You need at least 11 quarters for the out-of-sample test to start.
3. Run the two commands above for that company, then write up what you found in its `README.md`.

Good candidates have a consumer-facing KPI that people plausibly search for, and a reason the signal might behave differently from companies already covered.

## Limitations

- **Small samples.** Most companies have under 20 quarters of overlapping data. Treat results as directional, not as a trading model.
- **Searches are not customers.** Search interest mostly reflects discovery and buzz, not repeat usage.
- **Google Trends is relative and sampled.** Values are scaled 0 to 100 within each download and can shift slightly between downloads.
- **Worldwide search mixes markets.** Region-specific search terms (the `geo` field in `config.json`) are a natural next step.
