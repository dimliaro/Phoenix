# Phoenix

An ETL pipeline that pulls Premier League match data (2026/27 season) from the
[football-data.org](https://www.football-data.org/) API and loads it into a local
SQLite database. The pipeline is idempotent: it can be re-run at any time without
creating duplicates, and existing matches are updated as results come in.

## How it works

- **Extract:** calls the football-data.org API with an API key read from a `.env` file.
  If the request fails, the script stops with a non-zero exit code.
- **Transform:** flattens the nested JSON into one record per match (teams, scores,
  status, date) and validates types and missing values with pandas.
- **Load:** creates the `matches` table if it doesn't exist and writes the records
  with an upsert (`INSERT ... ON CONFLICT(id) DO UPDATE`).

## Database schema

Table `matches`, one row per match:

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key (match id from the API) |
| `utc_date` | TEXT | Kick-off time in UTC |
| `matchday` | INTEGER | Round of the season |
| `status` | TEXT | e.g. `FINISHED`, `TIMED`, `POSTPONED` |
| `home_team` / `away_team` | TEXT | Team short names |
| `ht_home_score` / `ht_away_score` | INTEGER | Half-time score, `NULL` if not played |
| `ft_home_score` / `ft_away_score` | INTEGER | Full-time score, `NULL` if not played |

On re-runs, only fields that can change (date, status, scores) are updated.

## How to run

1. Install dependencies: