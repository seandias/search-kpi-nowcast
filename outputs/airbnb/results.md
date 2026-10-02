# Airbnb (ABNB): search interest vs nights and experiences booked

- Quarters with both series (YoY): 15 (2022Q4 to 2026Q2)
- Correlation of YoY growth, search vs Nights booked: 0.71
- Out-of-sample quarters tested: 9
- Mean absolute error, naive benchmark: 1.87M
- Mean absolute error, search-change model: 1.70M (-9% vs benchmark)
- Mean absolute error, search-level model: 2.87M (+53% vs benchmark)
- Search-change model called acceleration vs deceleration correctly: 78% of quarters

## Walk-forward detail

| quarter   |   actual |   naive |   change_model |   level_model | actual_yoy   | naive_yoy   | change_yoy   | level_yoy   |
|:----------|---------:|--------:|---------------:|--------------:|:-------------|:------------|:-------------|:------------|
| 2024Q2    |    125.1 |   126   |          127.1 |         131.3 | 8.7%         | 9.5%        | 10.4%        | 14.1%       |
| 2024Q3    |    122.8 |   123   |          121.6 |         125.8 | 8.5%         | 8.7%        | 7.4%         | 11.1%       |
| 2024Q4    |    111   |   107.2 |          107.7 |         110.4 | 12.3%        | 8.5%        | 9.0%         | 11.7%       |
| 2025Q1    |    143.1 |   149   |          146.3 |         144.1 | 7.9%         | 12.3%       | 10.3%        | 8.7%        |
| 2025Q2    |    134.4 |   135   |          134.7 |         135.3 | 7.4%         | 7.9%        | 7.7%         | 8.1%        |
| 2025Q3    |    133.6 |   131.9 |          135.8 |         138.3 | 8.8%         | 7.4%        | 10.5%        | 12.6%       |
| 2025Q4    |    121.9 |   120.8 |          122.1 |         126.7 | 9.8%         | 8.8%        | 10.0%        | 14.1%       |
| 2026Q1    |    156.2 |   157.2 |          155.4 |         160   | 9.2%         | 9.8%        | 8.6%         | 11.8%       |
| 2026Q2    |    148.3 |   146.7 |          146   |         149.1 | 10.3%        | 9.2%        | 8.6%         | 10.9%       |

## Nowcast for 2026Q3 (not yet reported)

- Search interest YoY: -12.6%
- Naive benchmark: 147.4M (10.3% YoY)
- Search-change model: 142.0M (6.3% YoY)
- Search-level model: 140.1M (4.9% YoY)