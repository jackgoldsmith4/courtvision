import pandas as pd
import json
import os

team_codes = set()
player_names = os.listdir('./player_game_logs')
for name in player_names:
  file_path = './player_game_logs/' + name + '/' + name + '_RAW.csv'
  player_df = pd.read_csv(file_path)

  for code in player_df['Tm'].unique():
    team_codes.add(code)
  for code in player_df['Opp'].unique():
    team_codes.add(code)

if not os.path.exists('./constants'):
  os.mkdir('./constants')
with open('./constants/team_codes.py', 'w') as file:
  json.dump(list(team_codes), file)
