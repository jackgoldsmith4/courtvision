from utils import thread_func
import pandas as pd
import os

NUM_THREADS = 10

def clean_player_gamelog(filename):
  player_df = pd.read_csv(filename)

  # rename some cols for clarity
  player_df.rename(columns={
    'Unnamed: 5': 'Home/Away',
    'Unnamed: 7': 'Win/Loss',
    'Rk': 'Game of season',
    'G': 'Game for player',
    'Tm': 'Team',
    'Opp': 'Opponent',
    'Age': 'Age (days)',
    'GS': 'Game Started',
  }, inplace=True)

  # cleanup some of the columns
  player_df['Home/Away'].fillna('H', inplace=True)
  player_df['Home/Away'].replace('@','A', inplace=True)
  player_df['Date'] = pd.to_datetime(player_df['Date'])
  player_df['MP'] = convert_time_to_float(player_df['MP'])

  # convert age to days
  years, days = player_df['Age (days)'].str.split('-', expand=True).astype(int).values.T
  player_df['Age (days)'] = player_df['Age (days)'] = years * 365 + days

def clean_wrapper(filenames):
  for filename in filenames:
    print(f"Cleaning gamelog file: {filename}")
    clean_player_gamelog(filename)

def convert_time_to_float(time_series):
  split_series = time_series.str.split(':', expand=True)
  minutes = split_series[0].astype(int)
  seconds = split_series[1].astype(int)
  return round(minutes + seconds / 60, 2)

######## SCRIPT: run clean function on all NBA players
#thread_func(NUM_THREADS, clean_wrapper, os.listdir('./player_game_logs'))
filenames = os.listdir('./player_game_logs')
for name in filenames:
  df = pd.read_csv('./player_game_logs/' + name)
  if df.shape[0] < 100:
    pass # delete file
