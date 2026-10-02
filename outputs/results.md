# Results

- Quarters with both series (YoY): 13 (2022Q4 to 2026Q2)
- Correlation of YoY growth, search vs DAUs: 0.45
- Out-of-sample quarters tested: 7
- Mean absolute error, naive forecast (benchmark): 1.89M DAUs
- Mean absolute error, search-level model: 7.05M DAUs (+272% vs benchmark)
- Mean absolute error, search-change model: 1.97M DAUs (+4% vs benchmark)
- Search-change model called acceleration vs deceleration correctly: 43% of quarters

## Walk-forward detail

| quarter   |   actual_dau |   pred_dau |   naive_dau |   change_dau | actual_yoy   | pred_yoy   | naive_yoy   | change_yoy   |
|:----------|-------------:|-----------:|------------:|-------------:|:-------------|:-----------|:------------|:-------------|
| 2024Q4    |         40.5 |       42.7 |        41.4 |         41.2 | 50.6%        | 58.9%      | 53.7%       | 53.3%        |
| 2025Q1    |         46.6 |       49.7 |        47.3 |         47.1 | 48.4%        | 58.4%      | 50.6%       | 49.9%        |
| 2025Q2    |         47.7 |       53.3 |        50.6 |         50.8 | 39.9%        | 56.3%      | 48.4%       | 49.1%        |
| 2025Q3    |         50.5 |       57.5 |        52   |         52   | 35.8%        | 54.5%      | 39.9%       | 39.7%        |
| 2025Q4    |         52.7 |       61.6 |        55   |         55.1 | 30.1%        | 52.1%      | 35.8%       | 35.9%        |
| 2026Q1    |         56.5 |       68.4 |        60.6 |         61.1 | 21.2%        | 46.7%      | 30.1%       | 31.1%        |
| 2026Q2    |         58.7 |       69.3 |        57.8 |         57.7 | 23.1%        | 45.4%      | 21.2%       | 20.9%        |

## Nowcast for 2026Q3 (not yet reported)

- Search interest YoY: -12.8%
- Predicted DAUs: 69.4M (about ±7.1M), implying 37.4% YoY growth (search-level model)
- Predicted DAUs: 62.0M, implying 22.9% YoY growth (search-change model)