# Phoenix

An ETL pipeline that pulls Premier League match data (2026/27 season) from the
[football-data.org](https://www.football-data.org/) API and loads it into a local
SQLite database. The pipeline is idempotent: it can be re-run at any time without
creating duplicates, and existing matches are updated as results come in.

## How it works

- **`extract(url, headers)`:** calls the football-data.org API with an API key read
  from a `.env` file. If the request fails, the script stops with a non-zero exit code.
- **`transform(data)`:** flattens the nested JSON into one record per match and builds
  a pandas DataFrame with proper types (datetime for kick-off time, nullable integers
  for scores).
- **`load(db_path, df)`:** creates the `PremierLeague` table if it doesn't exist,
  converts the DataFrame into SQLite-compatible values (ISO date strings, `NULL` for
  missing scores) and writes it with an upsert (`INSERT ... ON CONFLICT(match_id) DO UPDATE`).

## Database schema

Table `PremierLeague`, one row per match:

| Column | Type | Notes |
|---|---|---|
| `match_id` | INTEGER | Primary key (match id from the API) |
| `match_date` | TEXT | Kick-off time in UTC, ISO 8601 |
| `matchday` | INTEGER | Round of the season |
| `status` | TEXT | e.g. `FINISHED`, `TIMED`, `POSTPONED` |
| `home_team` / `away_team` | TEXT | Team short names |
| `home_team_id` / `away_team_id` | INTEGER | Team ids from the API (stable keys for joins) |
| `ht_home_goals` / `ht_away_goals` | INTEGER | Half-time score, `NULL` if not played |
| `ft_home_goals` / `ft_away_goals` | INTEGER | Full-time score, `NULL` if not played |
| `winner` | TEXT | `HOME_TEAM`, `AWAY_TEAM`, `DRAW`, or `NULL` if not played |

On re-runs, only fields that can change (date, status, scores, winner) are updated.

## How to run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Get a free API key from football-data.org and create a `.env` file:
   ```
   FOOTBALLORG_API=your_key_here
   ```
3. Run the pipeline:
   ```
   python phoenix_refactored.py
   ```

This creates `premier_league.db` in the project folder.

## Roadmap

- Add a `main()` entry point so functions can be imported without running the pipeline
- Add logging and basic data quality checks
- Integrate xG data from Understat (team mapping + match matching)
- Schedule daily runs
- Containerize with Docker

## Notes

Built as a hands-on learning project, with Claude as a tutor (hints and code
review; the code is written by me).