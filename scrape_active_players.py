from selenium.webdriver.common.by import By
from utils import init_web_driver
import pandas as pd
import string
import re

def create_br_url_id(player_name):
  player_name = player_name.lower().split(' ')
  last_name_id = player_name[1][:5] if len(player_name[1]) > 4 else player_name[1]
  return player_name[1][0] + '/' + last_name_id + player_name[0][:2]

driver = init_web_driver()

lowercase_letters = list(string.ascii_lowercase)
active_players = []
for letter in lowercase_letters:
  driver.get("https://www.basketball-reference.com/players/" + letter)
  names = driver.find_elements(By.TAG_NAME, 'strong')
  for elem in names:
    txt = elem.find_element(By.XPATH, '../..').text
    if txt == '' or 'Last Names Starting' in txt:
      continue
    elif 'Players' in txt:
      break
    
    # parse each row
    player_name = ''
    rookie_year = -1
    is_active_flag = False
    for elem in txt.split():
      if is_active_flag:
        if elem == '2024':
          active_players.append((player_name[:-1], rookie_year))
        is_active_flag = False
        break

      if not elem.isnumeric():
        player_name += elem + ' '
      else:
        rookie_year = elem
        is_active_flag = True

# store active_players as a DataFrame
active_players_df = pd.DataFrame(active_players, columns=['Name', 'Rookie Year'])

# generate player ID's for basketball-reference scraping
active_players_df['Basketball-Reference URL ID'] = active_players_df['Name'].apply(lambda x: create_br_url_id(x))

# for non-unique name ids, enumerate like B-R does (e.g. Mikal Bridges and Miles Bridges, both "bridgmi")
non_unique_ids = active_players_df['Basketball-Reference URL ID'][active_players_df['Basketball-Reference URL ID'].duplicated(keep=False)].unique()
for value in non_unique_ids:
  mask = active_players_df['Basketball-Reference URL ID'] == value
  for i, index in enumerate(active_players_df[mask].index, start=1):
    active_players_df.at[index, 'Basketball-Reference URL ID'] = f"{active_players_df.at[index, 'Basketball-Reference URL ID']}{i:02d}"

# for all other name ids, add "01" in accordance with B-R ID system
for index, row in active_players_df.iterrows():
  if not bool(re.search(r'\d$', row['Basketball-Reference URL ID'])):
      active_players_df.at[index, 'Basketball-Reference URL ID'] += '01'

# drop dupes and save updated list of active players
active_players_df.drop_duplicates(inplace=True)
active_players_df.to_csv('active_players.csv', index=False)
