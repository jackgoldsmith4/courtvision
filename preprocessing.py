from sklearn.model_selection import train_test_split
from constants.team_codes import TEAM_CODES
from sqlalchemy import create_engine
from db.player_stats import get_flattened_player_stats_by_game_id
from utils import thread_func
import pandas as pd
import shutil
import os
from datetime import date

NUM_THREADS = 1

def preprocess_player_gamelog(file_path):
  player_df = pd.read_csv(file_path)

  # drop any inactive games (if missed by scrape)
  player_df = player_df.dropna(subset=['G'])

  # delete the directory if this player has played fewer than 100 games
  if player_df.shape[0] < 100:
    parent_dir = os.path.dirname(file_path)
    shutil.rmtree(parent_dir)
    return

  # rename some cols for clarity
  player_df.rename(columns={
    'Unnamed: 5': 'Home?',
    'Unnamed: 7': 'Win/Loss',
    'Rk': 'Game of season',
    'G': 'Game for player',
    'Tm': 'Team',
    'Opp': 'Opponent',
    'Age': 'Age (days)',
    'GS': 'Game Started?',
    'MP': 'Minutes Played',
  }, inplace=True)

  # cleanup some of the columns
  player_df['Home?'].fillna(1, inplace=True)
  player_df['Home?'].replace('@',0, inplace=True)
  player_df['Date'] = pd.to_datetime(player_df['Date'])
  player_df = player_df.dropna(subset=['Minutes Played'])
  #player_df['Minutes Played'] = convert_time_to_float(player_df['Minutes Played'])

  # convert age to days
  years, days = player_df['Age (days)'].str.split('-', expand=True).astype(int).values.T
  player_df['Age (days)'] = player_df['Age (days)'] = years * 365 + days

  # add date features
  player_df['Date'] = pd.to_datetime(player_df['Date'])
  player_df['Year'] = player_df['Date'].dt.year
  player_df['Month of Season'] = player_df['Date'].dt.month.apply(get_seasonal_month)

  # # extract 'Win?' and 'Victory Margin' from 'Win/Loss'
  # player_df['Win?'] = 0
  # player_df = player_df.apply(modify_win_loss_row, axis=1)
  # player_df['Victory Margin'] = player_df['Win/Loss'].str.extract(r'\(([+-]?\d+)\)').astype(int)

  # one-hot encode Team and Opponent columns
  for team in TEAM_CODES:
    player_df['Team_' + team] = 0
    player_df['Opponent_' + team] = 0
  player_df = player_df.apply(encode_team_row, axis=1)

  # drop cols that won't be used in the model
  player_df.drop(
    columns=['Date', 'Team', 'Opponent', 'Win/Loss', 'Minutes Played', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'GmSc', '+/-'],
    inplace=True
  )

  # 80/20 random train/test split
  train_df, test_df = train_test_split(player_df, test_size=0.2, random_state=42)

  # save preprocessed files
  train_df.to_csv(file_path.replace('RAW', 'TRAIN'), index=False)
  test_df.to_csv(file_path.replace('RAW', 'TEST'), index=False)

def preprocess_wrapper(player_names):
  for name in player_names:
    print(f"Processing gamelog file: {name}")
    file_path = './player_game_logs/' + name + '/' + name + '_RAW.csv'
    preprocess_player_gamelog(file_path)

# Helper: convert time in mm:ss format to a float
def convert_time_to_float(time_series):
  split_series = time_series.str.split(':', expand=True)
  minutes = split_series[0].astype(int)
  seconds = split_series[1].astype(int)
  return round(minutes + seconds / 60, 2)

# Helper: get month of the season (starting in October)
def get_seasonal_month(month):
  if month >= 10:
    return month - 9
  else:
    return month + 3

# Helper: change row's Win? column to 1 if that game was a win
def modify_win_loss_row(row):
  win_loss = row['Win/Loss'].str.extract(r'([WL])')
  if win_loss == 'W':
    row['Win?'] = 1
  return row

# Helper: one-hot encode one row of the DF for Team and Opponent
def encode_team_row(row):
  team = row['Team']
  opponent = row['Opponent']
  row['Team_' + team] = 1
  row['Opponent_' + opponent] = 1
  return row

######## SCRIPT: run clean function on all NBA players
#thread_func(NUM_THREADS, preprocess_wrapper, os.listdir('./player_game_logs'))

engine = create_engine("postgresql://bgzcpelsdernwi:b0ee04605f43866313250fad7a64d9f0299acf0d7d933e486b062a124a34085d@ec2-54-156-185-205.compute-1.amazonaws.com:5432/d5g89ferun7sda")
get_flattened_player_stats_by_game_id(engine, date(2011, 2, 8), 'Indiana Pacers', 'Miami Heat')
