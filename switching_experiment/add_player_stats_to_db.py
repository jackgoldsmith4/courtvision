from utils import convert_time_to_float, thread_func
from db.player_stats import insert_player_stat
from constants.team_codes import TEAM_CODES
from sqlalchemy import create_engine
from datetime import datetime
import pandas as pd
import os

def add_player_stats_to_db(files):
  engine = create_engine("postgresql://bgzcpelsdernwi:b0ee04605f43866313250fad7a64d9f0299acf0d7d933e486b062a124a34085d@ec2-54-156-185-205.compute-1.amazonaws.com:5432/d5g89ferun7sda")
  for file_name in files:
      player_df = pd.read_csv(f"./player_game_logs/{file_name}/{file_name}_RAW.csv")
      player_name = ' '.join(file_name.split('_')).title()
      for index, row in player_df.iterrows():
        try:
          try:
            game_date = datetime.strptime(row.Date, "%Y-%m-%d").date()
          except:
            game_date = datetime.strptime(row.Date, "%Y-%m-%d")

          is_home_game = 1
          if row['Unnamed: 5'] == '@':
            is_home_game = 0

          home_team = ''
          away_team = ''
          if is_home_game == 1:
            home_team = TEAM_CODES[row['Tm']]
            away_team = TEAM_CODES[row['Opp']]
          else:
            home_team = TEAM_CODES[row['Opp']]
            away_team = TEAM_CODES[row['Tm']]
          
          years, days = row['Age'].split('-')
          player_age = 365*int(years) + int(days)
          game_started = int(row['GS'])
          wl, margin = row['Unnamed: 7'].split(' (')
          margin = int(margin[1:-1])
          game_outcome = 0
          if wl == 'W':
            game_outcome = margin
          else:
            game_outcome = -margin

          try:
            plus_minus=int(row['+/-'])
          except ValueError:
            plus_minus=0

          insert_player_stat(
            engine,
            game_date=game_date,
            home_team=home_team,
            away_team=away_team,
            is_home_game=is_home_game,
            player_name=player_name,
            player_age=player_age,
            game_started=game_started,
            game_outcome=game_outcome,
            minutes_played=convert_time_to_float(row['MP']),
            points=int(row['PTS']),
            fg_made=int(row['FG']),
            fg_attempted=int(row['FGA']),
            threes_made=int(row['3P']),
            threes_attempted=int(row['3PA']),
            ft_made=int(row['FT']),
            ft_attempted=int(row['FTA']),
            orb=int(row['ORB']),
            drb=int(row['DRB']),
            assists=int(row['AST']),
            steals=int(row['STL']),
            blocks=int(row['BLK']),
            turnovers=int(row['TOV']),
            plus_minus=plus_minus
          )
        except:
          # player didn't play in this game and should be added with zeroes
          insert_player_stat(
            engine,
            game_date=game_date,
            home_team=home_team,
            away_team=away_team,
            is_home_game=is_home_game,
            player_name=player_name,
            player_age=player_age,
            game_started=0,
            game_outcome=game_outcome,
            minutes_played=0.0,
            points=0,
            fg_made=0,
            fg_attempted=0,
            threes_made=0,
            threes_attempted=0,
            ft_made=0,
            ft_attempted=0,
            orb=0,
            drb=0,
            assists=0,
            steals=0,
            blocks=0,
            turnovers=0,
            plus_minus=0
          )        

  engine.dispose()

NUM_THREADS = 10
thread_func(NUM_THREADS, add_player_stats_to_db, os.listdir('./player_game_logs'))
