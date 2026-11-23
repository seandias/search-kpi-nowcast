# Airbnb (ABNB): search interest vs nights and experiences booked

- Quarters with both series (YoY): 20 (2021Q4 to 2026Q3)
- Correlation of YoY growth, search vs Nights booked: 0.73
- Out-of-sample quarters tested: 14
- Mean absolute error, naive benchmark: 2.80M
- Mean absolute error, search-change model: 3.07M (+9% vs benchmark)
- Mean absolute error, search-level model: 7.14M (+155% vs benchmark)
- Search-change model called acceleration vs deceleration correctly: 57% of quarters
- Search-change model closer than the benchmark: 6 of 14 quarters
- Search-change vs benchmark without its single best quarter: +25%

## Walk-forward detail

| quarter   |   actual |   naive |   change_model |   level_model | actual_yoy   | naive_yoy   | change_yoy   | level_yoy   |
|:----------|---------:|--------:|---------------:|--------------:|:-------------|:------------|:-------------|:------------|
| 2023Q2    |    115.1 |   123   |          120.7 |         120.6 | 11.0%        | 18.6%       | 16.4%        | 16.3%       |
| 2023Q3    |    113.2 |   110.7 |          111.3 |         114.9 | 13.5%        | 11.0%       | 11.6%        | 15.3%       |
| 2023Q4    |     98.8 |   100.1 |          101.5 |         104.2 | 12.0%        | 13.5%       | 15.1%        | 18.2%       |
| 2024Q1    |    132.6 |   135.7 |          136.5 |         143.6 | 9.5%         | 12.0%       | 12.7%        | 18.6%       |
| 2024Q2    |    125.1 |   126   |          126.3 |         135.6 | 8.7%         | 9.5%        | 9.7%         | 17.8%       |
| 2024Q3    |    122.8 |   123   |          121.9 |         129.4 | 8.5%         | 8.7%        | 7.7%         | 14.3%       |
| 2024Q4    |    111   |   107.2 |          106.9 |         111.4 | 12.3%        | 8.5%        | 8.2%         | 12.8%       |
| 2025Q1    |    143.1 |   149   |          144.4 |         138.3 | 7.9%         | 12.3%       | 8.9%         | 4.3%        |
| 2025Q2    |    134.4 |   135   |          134.6 |         130.4 | 7.4%         | 7.9%        | 7.6%         | 4.3%        |
| 2025Q3    |    133.6 |   131.9 |          137   |         141.1 | 8.8%         | 7.4%        | 11.6%        | 14.9%       |
| 2025Q4    |    121.9 |   120.8 |          122.3 |         130.8 | 9.8%         | 8.8%        | 10.2%        | 17.8%       |
| 2026Q1    |    156.2 |   157.2 |          156   |         165.1 | 9.2%         | 9.8%        | 9.0%         | 15.4%       |
| 2026Q2    |    148.3 |   146.7 |          145.6 |         151.9 | 10.3%        | 9.2%        | 8.4%         | 13.1%       |
| 2026Q3    |    155   |   147.4 |          140.6 |         133.8 | 16.0%        | 10.3%       | 5.2%         | 0.2%        |