from selenium.webdriver.common.by import By
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.players import insert_player
from utils import init_web_driver
import pandas as pd
import string
import time
import os

engine = create_engine(os.getenv("DATABASE_URI"))
Session = sessionmaker(bind=engine)
session = Session()

driver = init_web_driver()
driver.implicitly_wait(2)

lowercase_letters = list(string.ascii_lowercase)
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
        end_year = elem
        insert_player(session, player_id, player_name, rookie_year, end_year)
        break

      if not elem.isnumeric():
        player_name += elem + ' '
      else:
        rookie_year = elem
        name_final_flag = True

session.close()
engine.dispose()
