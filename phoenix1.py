import pandas as pd
import requests
import sqlite3
import os
import sys
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('FOOTBALLORG_API')    
headers = {'X-Auth-Token':key}

response = requests.get("https://api.football-data.org/v4/competitions/PL/matches",headers = headers)

if(response.status_code==200):
    status = "OK"
    data = response.json()
    print(f'Status {status}')
else:
    print(f'Error! {response.status_code} code')
    sys.exit(1)




matches = []

for match in data["matches"]:
    id = match["id"]
    date = match["utcDate"]
    matchday = match["matchday"]
    status = match["status"]
    home_team = match["homeTeam"]["shortName"]
    away_team = match["awayTeam"]["shortName"]
    ht_home_score = match["score"]["halfTime"]["home"]
    ht_away_score = match["score"]["halfTime"]["away"]
    ft_home_score = match["score"]["fullTime"]["home"]
    ft_away_score = match["score"]["fullTime"]["away"]
    matches.append({
        "id":id,
        "utc_date":date,
        "matchday":matchday,
        "status":status,
        "home_team": home_team,
        "away_team": away_team,
        "ht_home_score": ht_home_score,
        "ht_away_score": ht_away_score,
        "ft_home_score": ft_home_score,
        "ft_away_score": ft_away_score
    })

df = pd.DataFrame(matches)

df["utc_date"] = pd.to_datetime(df["utc_date"])
df["ht_home_score"]=df["ht_home_score"].astype('Int64')
df["ht_away_score"]=df["ht_away_score"].astype('Int64')
df["ft_home_score"]=df["ft_home_score"].astype('Int64')
df["ft_away_score"]=df["ft_away_score"].astype('Int64')


conn = sqlite3.connect('football.db')
create_table = """
create table if not exists matches(
id INTEGER PRIMARY KEY not null,
utc_date text ,
matchday INTEGER,
home_team TEXT not null,
away_team TEXT not null,
ht_home_score INTEGER,
ft_home_score INTEGER,
ht_away_score INTEGER,
ft_away_score INTEGER,
status text)

"""
conn.execute(create_table)


upsert = """
insert into matches (id,utc_date, matchday, status, home_team,away_team,ht_away_score,ht_home_score,ft_away_score,ft_home_score)
values  (:id,:utc_date,:matchday,:status, :home_team, :away_team, :ht_away_score, :ht_home_score, :ft_away_score, :ft_home_score)
on conflict(id) do UPDATE set 
	utc_date = excluded.utc_date,
	status = excluded.status,
	ht_away_score = excluded.ht_away_score,
	ht_home_score = excluded.ht_home_score,
	ft_away_score = excluded.ft_away_score,
	ft_home_score = excluded.ft_home_score;
"""

conn.executemany(upsert,matches)
conn.commit()

print(pd.read_sql("""

select count(*) from matches

""",conn))