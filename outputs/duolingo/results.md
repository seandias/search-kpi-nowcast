# Duolingo (DUOL): search interest vs daily active users (daus)

- Quarters with both series (YoY): 17 (2022Q3 to 2026Q3)
- Correlation of YoY growth, search vs DAUs: 0.53
- Out-of-sample quarters tested: 11
- Mean absolute error, naive benchmark: 1.86M
- Mean absolute error, search-change model: 1.78M (-4% vs benchmark)
- Mean absolute error, search-level model: 5.59M (+200% vs benchmark)
- Search-change model called acceleration vs deceleration correctly: 64% of quarters
- Search-change model closer than the benchmark: 7 of 11 quarters
- Search-change vs benchmark without its single best quarter: -0%

## Walk-forward detail

| quarter   |   actual |   naive |   change_model |   level_model | actual_yoy   | naive_yoy   | change_yoy   | level_yoy   |
|:----------|---------:|--------:|---------------:|--------------:|:-------------|:------------|:-------------|:------------|
| 2024Q1    |     31.4 |    33.5 |           33   |          33.8 | 54.7%        | 65.0%       | 62.6%        | 66.6%       |
| 2024Q2    |     34.1 |    33.1 |           33.5 |          34.5 | 59.3%        | 54.7%       | 56.6%        | 61.0%       |
| 2024Q3    |     37.2 |    38.6 |           38.5 |          38.9 | 53.7%        | 59.3%       | 58.9%        | 60.7%       |
| 2024Q4    |     40.5 |    41.4 |           41.6 |          42.8 | 50.6%        | 53.7%       | 54.7%        | 59.2%       |
| 2025Q1    |     46.6 |    47.3 |           47.7 |          49.7 | 48.4%        | 50.6%       | 51.9%        | 58.3%       |
| 2025Q2    |     47.7 |    50.6 |           50.3 |          53.5 | 39.9%        | 48.4%       | 47.5%        | 57.0%       |
| 2025Q3    |     50.5 |    52   |           52.4 |          57.7 | 35.8%        | 39.9%       | 40.8%        | 55.2%       |
| 2025Q4    |     52.7 |    55   |           54.8 |          61.9 | 30.1%        | 35.8%       | 35.4%        | 52.9%       |
| 2026Q1    |     56.5 |    60.6 |           59.9 |          68.8 | 21.2%        | 30.1%       | 28.6%        | 47.7%       |
| 2026Q2    |     58.7 |    57.8 |           58.7 |          70   | 23.1%        | 21.2%       | 23.1%        | 46.7%       |
| 2026Q3    |     64.9 |    62.1 |           61.1 |          70.6 | 28.5%        | 23.1%       | 20.9%        | 39.7%       |