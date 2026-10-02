# Duolingo (DUOL): search interest vs daily active users (daus)

- Quarters with both series (YoY): 13 (2022Q4 to 2026Q2)
- Correlation of YoY growth, search vs DAUs: 0.45
- Out-of-sample quarters tested: 7
- Mean absolute error, naive benchmark: 1.89M
- Mean absolute error, search-change model: 1.97M (+4% vs benchmark)
- Mean absolute error, search-level model: 7.05M (+272% vs benchmark)
- Search-change model called acceleration vs deceleration correctly: 43% of quarters

## Walk-forward detail

| quarter   |   actual |   naive |   change_model |   level_model | actual_yoy   | naive_yoy   | change_yoy   | level_yoy   |
|:----------|---------:|--------:|---------------:|--------------:|:-------------|:------------|:-------------|:------------|
| 2024Q4    |     40.5 |    41.4 |           41.2 |          42.7 | 50.6%        | 53.7%       | 53.3%        | 58.9%       |
| 2025Q1    |     46.6 |    47.3 |           47.1 |          49.7 | 48.4%        | 50.6%       | 49.9%        | 58.4%       |
| 2025Q2    |     47.7 |    50.6 |           50.8 |          53.3 | 39.9%        | 48.4%       | 49.1%        | 56.3%       |
| 2025Q3    |     50.5 |    52   |           52   |          57.5 | 35.8%        | 39.9%       | 39.7%        | 54.5%       |
| 2025Q4    |     52.7 |    55   |           55.1 |          61.6 | 30.1%        | 35.8%       | 35.9%        | 52.1%       |
| 2026Q1    |     56.5 |    60.6 |           61.1 |          68.4 | 21.2%        | 30.1%       | 31.1%        | 46.7%       |
| 2026Q2    |     58.7 |    57.8 |           57.7 |          69.3 | 23.1%        | 21.2%       | 20.9%        | 45.4%       |

## Nowcast for 2026Q3 (not yet reported)

- Search interest YoY: -12.8%
- Naive benchmark: 62.1M (23.1% YoY)
- Search-change model: 62.0M (22.9% YoY)
- Search-level model: 69.4M (37.4% YoY)