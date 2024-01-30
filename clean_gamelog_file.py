from utils import thread_func
import pandas as pd
import shutil
import os

NUM_THREADS = 1

def clean_player_gamelog(file_path):
  player_df = pd.read_csv(file_path)

  # drop any inactive games (if missed by scrape)
  player_df = player_df.dropna(subset=['G'])

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
  }, inplace=True)

  # cleanup some of the columns
  player_df['Home?'].fillna(1, inplace=True)
  player_df['Home?'].replace('@',0, inplace=True)
  player_df['Date'] = pd.to_datetime(player_df['Date'])
  player_df = player_df.dropna(subset=['MP'])
  player_df['MP'] = convert_time_to_float(player_df['MP'], file_path)

  # convert age to days
  years, days = player_df['Age (days)'].str.split('-', expand=True).astype(int).values.T
  player_df['Age (days)'] = player_df['Age (days)'] = years * 365 + days

  player_df.to_csv(file_path, index=False)

def clean_wrapper(player_names):
  for name in player_names:
    print(f"Cleaning gamelog file: {name}")
    file_path = './player_game_logs/' + name + '/' + name + '.csv'
    clean_player_gamelog(file_path)

def convert_time_to_float(time_series, file_path):
  split_series = time_series.str.split(':', expand=True)
  minutes = split_series[0].astype(int)
  seconds = split_series[1].astype(int)
  return round(minutes + seconds / 60, 2)

######## SCRIPT: run clean function on all NBA players
thread_func(NUM_THREADS, clean_wrapper, os.listdir('./player_game_logs'))
