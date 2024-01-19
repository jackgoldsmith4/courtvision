from selenium.webdriver.common.by import By
from utils import init_web_driver
import pandas as pd
import string

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

# store active_players as series
active_players_df = pd.DataFrame(active_players, columns=['Name', 'Rookie Year'])
active_players_df.to_csv('active_players.csv')
