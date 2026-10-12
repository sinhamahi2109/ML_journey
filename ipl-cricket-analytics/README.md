# IPL Cricket Analytics (2008-2025)

**Live app:** https://ipl-cricket-analytics.streamlit.app/

An end-to-end analytics project on every ball bowled in the IPL from 2008 to 2025:
1,169 matches and 278,205 deliveries. The analysis is written in SQL (MySQL),
and an interactive Streamlit app on top of it lets anyone explore batting, bowling,
teams and venues.

## Tech stack
MySQL, SQL (JOINs, CTEs, window functions, subqueries), Python, pandas, SQLite, Streamlit

## Key findings
- Scoring has changed: average runs per match went from 309.3 in 2007/08 to 358.5 in 2025.
- Phase of the innings: the run rate is 7.96 in the powerplay and 10.02 in the death overs.
- Virat Kohli is the all-time leading run scorer with 8,671 runs, and Chris Gayle has hit the most sixes (359).
- Yuzvendra Chahal has taken the most wickets (221).
- Chennai Super Kings has the best win percentage (56.3%) among teams with 50+ matches.
- Winning the toss is only a small advantage: toss winners won 51.6% of matches.
- Arun Jaitley Stadium, Delhi has the highest average first-innings score (200.3).

## What is in this repo
| File | Purpose |
|---|---|
| `00_basic_setup.sql` - `01_setup_and_cleaning.sql` | Database setup and data cleaning (standardising renamed team names) |
| `02_basic_queries.sql` | Matches per season, team wins, toss impact, venues, top run scorers |
| `03_batting_bowling_queries.sql` | Sixes, strike rates, wickets, dot balls |
| `04_joins_and_window_functions.sql` | JOINs, subqueries, and a window function (top scorer of every season) |
| `05_advanced_queries.sql` | Phase run rates, head-to-head records, win percentages, venue averages |
| `app.py` | Streamlit app that runs the same analysis on a SQLite copy of the data |
| `ipl.db.zip` | Compressed SQLite database used by the app |

## Data quality check
After loading the data into MySQL, I compared the number of matches in the matches table
against the number of distinct matches in the ball-by-ball table. They did not match
(1,099 vs 1,169): the import wizard had silently dropped 70 matches. I confirmed the source
file was complete and reloaded the table, so all results use the full 1,169 matches.

## Run it locally
pip install -r requirements.txt
streamlit run app.py

## Data source
Kaggle: "IPL Ball By Ball 2008 to 2025" (dgsports).
