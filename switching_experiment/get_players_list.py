import pandas as pd

players_df = pd.read_csv('./nba_players.csv')

player_names = list(players_df['Name'])
player_names = [name.split(' ') for name in player_names]
player_names = [item for sublist in player_names for item in sublist]
print(list(set(player_names)))
print(len(player_names))