from selenium.webdriver.common.by import By
from utils import init_web_driver
import pandas as pd
import time

def scrape_game_log(player_name, rookie_year):
  driver = init_web_driver()
  
  player_name = player_name.lower().split(' ')
  output_file_name = player_name[0] + '_' + player_name[1]
  # TODO: account for Miles/Mikal Bridges - they have the same ID and are labeled 01/02 in the URL
  last_name_id = player_name[1][:5] if len(player_name[1]) > 4 else player_name[1]
  player_url_id = player_name[1][0] + '/' + last_name_id + player_name[0][:2]
  url = 'https://www.basketball-reference.com/players/' + player_url_id + '01/gamelog/'

  for year in range(int(rookie_year), 2025):
    driver.get(url + str(year))
    
    # find game log elem, turn to csv table
    # if a file doesn't exist with this player's name, create one and populate with col headers and this season
    # if it does exist, just populate with this season's CSV, no headers

scrape_game_log("Stephen Curry", '2022')
