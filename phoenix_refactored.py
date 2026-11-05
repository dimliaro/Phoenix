
import os,sys
import pandas as pd
from dotenv import load_dotenv
import requests
import sqlite3 
load_dotenv() 
pl_db = 'premier_league.db'
 
url = 'https://api.football-data.org/v4/competitions/PL/matches'
headers = {
    'X-Auth-Token': os.getenv('FOOTBALLORG_API')
}
def extract(url,headers):
    res = requests.get(url,headers=headers)
    if(res.status_code==200):
        data = res.json()
        print(f'Data retrieved! Status: {res.status_code }')
    else:
        print(f"Error retrieving data!: {res.status_code} code")
        sys.exit(1)

    return data

def transform(data):
    matches = []
    for match in data["matches"]:
        match_id=match['id']
        home_team = match['homeTeam']['shortName']
        away_team = match['awayTeam']['shortName']
        ft_home_goals = match['score']['fullTime']['home']
        ft_away_goals = match['score']['fullTime']['away']
        ht_home_goals = match['score']['halfTime']['home']
        ht_away_goals = match['score']['halfTime']['away']
        status = match['status']
        home_team_id = match['homeTeam']['id']
        away_team_id = match['awayTeam']['id']
        matchday = match['matchday']
        match_date = match['utcDate']
        winner = match['score']['winner']
        matches.append(
            {
                "match_id":match_id,
                "home_team":home_team,
                "away_team":away_team,
                "ft_home_goals":ft_home_goals,
                "ft_away_goals":ft_away_goals,
                "ht_home_goals":ht_home_goals,
                "ht_away_goals":ht_away_goals,
                "status":status,
                "matchday":matchday,
                'match_date':match_date,
                'home_team_id':home_team_id,
                'away_team_id':away_team_id,
                'winner':winner

            }
        )
    df = pd.DataFrame(matches)
    df["match_date"] = pd.to_datetime(df["match_date"])
    df["ht_home_goals"]=df["ht_home_goals"].astype('Int64')
    df["ht_away_goals"]=df["ht_away_goals"].astype('Int64')
    df["ft_home_goals"]=df["ft_home_goals"].astype('Int64')
    df["ft_away_goals"]=df["ft_away_goals"].astype('Int64')
   
    
    

    return df

def load(pl_db,df):
    conn = sqlite3.connect(pl_db)
    creation = """
        create table if not exists PremierLeague(
        match_id INTEGER PRIMARY KEY not null,
        match_date text,
        matchday INTEGER,
        home_team TEXT not null,
        away_team TEXT not null,
        ht_home_goals INTEGER,
        ft_home_goals INTEGER,
        ht_away_goals INTEGER,
        ft_away_goals INTEGER,
        home_team_id INTEGER not null,
        away_team_id INTEGER not null,
        winner TEXT, 
        status text)
    """
    conn.execute(creation)
    upsert = """

        INSERT INTO PremierLeague (match_id,home_team,away_team,ft_home_goals,ft_away_goals,ht_home_goals,
        ht_away_goals,status,matchday,match_date,home_team_id,away_team_id,winner)
        VALUES(:match_id,:home_team,:away_team,:ft_home_goals,:ft_away_goals,:ht_home_goals,
        :ht_away_goals,:status,:matchday,:match_date,:home_team_id,:away_team_id,:winner)
        ON CONFLICT(match_id) do update set 

        status = excluded.status,
        match_date = excluded.match_date,
        ht_away_goals = excluded.ht_away_goals,
        ht_home_goals = excluded.ht_home_goals,
        ft_away_goals = excluded.ft_away_goals,
        ft_home_goals = excluded.ft_home_goals,
        winner = excluded.winner;
     """
    df["match_date"] = df["match_date"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df = df.astype(object).where(df.notna(), None)
    df = df.to_dict('records')

    conn.executemany(upsert,df)
    conn.commit()
    count = pd.read_sql("""

            select count(*) from PremierLeague

        """,conn)
    print(count)



if __name__ == "__main__":

    ex = extract(url,headers)
    tr = transform(ex)
    load(pl_db,tr)


