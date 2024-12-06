from selenium.webdriver.common.by import By
from utils import init_web_driver
import pandas as pd
import string
import time

driver = init_web_driver()
driver.implicitly_wait(2)

lowercase_letters = list(string.ascii_lowercase)
players = []
for letter in lowercase_letters:
  print(f"Scraping players beginning with {letter}...")
  driver.get("https://www.basketball-reference.com/players/" + letter)
  time.sleep(2)
  players_table = driver.find_element(By.XPATH, '//*[contains(text(), "Birth Date")]/../../..')
  player_elems = players_table.find_elements(By.TAG_NAME, 'tr')
  for elem in player_elems:
    txt = elem.text
    if 'Player' in txt:
      continue

    player_id = letter + '/' + elem.find_element(By.TAG_NAME, 'th').get_attribute('data-append-csv')

    # parse each row
    player_name = ''
    rookie_year = -1
    name_final_flag = False
    for elem in txt.split():
      if name_final_flag:
        players.append((player_name[:-1].replace('*', ''), player_id, rookie_year, elem))
        break

      if not elem.isnumeric():
        player_name += elem + ' '
      else:
        rookie_year = elem
        name_final_flag = True

# store active_players as a CSV file
players_df = pd.DataFrame(players, columns=['Name', 'Basketball-Reference URL ID', 'Rookie Year', 'Final Year'])
players_df.drop_duplicates(inplace=True)
players_df.to_csv('nba_players.csv', index=False)
