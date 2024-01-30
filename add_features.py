from constants import team_binary_encodings
from utils import thread_func
import pandas as pd
import shutil
import os

def get_seasonal_month(month):
  if month >= 10:
    return month - 9
  else:
    return month + 3

def add_features(name):
  file_path = './player_game_logs/' + name + '/' + name + '.csv'
  player_df = pd.read_csv(file_path)

  # skip over files to which features have already been added
  if 'Team_Encoded_0' in player_df.columns:
    return

  # Add date features
  player_df['Date'] = pd.to_datetime(player_df['Date'])
  player_df['Year'] = player_df['Date'].dt.year
  player_df['Month of Season'] = player_df['Date'].dt.month.apply(get_seasonal_month)

  # Extract 'Win?' and 'Victory Margin' from 'Win/Loss'
  player_df['Win?'] = player_df['Win/Loss'].str.extract(r'([WL])')
  player_df['Victory Margin'] = player_df['Win/Loss'].str.extract(r'\(([+-]?\d+)\)').astype(int)
  player_df.drop(columns=['Win/Loss'], inplace=True)

  # Standardize team codes for different eras
  if ('KCK' in player_df['Team'].values) | ('KCK' in player_df['Opponent'].values):
    shutil.rmtree(file_path.replace('/' + name + '.csv', ''))
    return
  player_df['Team'] = player_df['Team'].str.replace('WSB', 'WSH')
  player_df['Opponent'] = player_df['Opponent'].str.replace('WSB', 'WSH')
  player_df['Team'] = player_df['Team'].str.replace(r'\b(NJN|BRK|BKN)\b', 'NETS', regex=True)
  player_df['Opponent'] = player_df['Opponent'].str.replace(r'\b(NJN|BRK|BKN)\b', 'NETS', regex=True)
  player_df['Team'] = player_df['Team'].str.replace(r'^NO[H|P]', 'NO', regex=True)
  player_df['Opponent'] = player_df['Opponent'].str.replace(r'^NO[H|P]', 'NO', regex=True)

  # Binary encode Team and Opponent cols (compromise for LinReg and tree regression)
  player_df['Team_Encoded'] = player_df['Team'].map(team_binary_encodings)
  player_df['Opponent_Encoded'] = player_df['Opponent'].map(team_binary_encodings)
  player_df[['Team_Encoded_'+str(i) for i in range(5)]] = player_df['Team_Encoded'].apply(pd.Series)
  player_df[['Opponent_Encoded_'+str(i) for i in range(5)]] = player_df['Opponent_Encoded'].apply(pd.Series)
  player_df.drop(columns=['Team_Encoded', 'Opponent_Encoded'], inplace=True)

  player_df.to_csv(file_path, index=False)

def add_features_wrapper(player_names):
  for name in player_names:
    print(f"Adding features: {name}")
    add_features(name)

NUM_THREADS = 1
thread_func(NUM_THREADS, add_features_wrapper, os.listdir('./player_game_logs'))
