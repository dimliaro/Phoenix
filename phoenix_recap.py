import requests
import pandas as pd
from dotenv import load_dotenv
import os , sys


load_dotenv()
api_key = os.getenv('FOOTBALLORG_API')
headers = {'X-Auth-Token':api_key}

res = requests.get(url='https://api.football-data.org/v4/competitions/PL/matches', headers = headers)

if(res.status_code==200):
    data = res.json()
    print(f"Data retrieved! Status : {res.status_code}")
else:
    print(f"Error {res.status_code} code.")
    sys.exit(1)

matches = []
for match in data["matches"]:
    id = match['id']
    status = match['status']
    matchday = match['matchday']
    match_date = match['utcDate']
    home_goals = match['score']['fullTime']['home']
    away_goals = match['score']['fullTime']['away']
    home_team = match['homeTeam']['shortName']
    away_team = match['awayTeam']['shortName']
    matches.append(
        {"id":id,
         'homeTeam':home_team,
         'awayTeam':away_team,
         'FTHG':home_goals,
         'FTAG':away_goals,
         'matchday':matchday,
         'match_date':match_date,
         'status':status

         }
    )


df = pd.DataFrame(matches)
df['FTAG'] = df['FTAG'].astype('Int64')
df['FTHG'] = df['FTHG'].astype('Int64')
df['match_date'] = pd.to_datetime(df['match_date'])
pd.set_option('display.width', 200)
print(df.shape)
print(df.head(1))