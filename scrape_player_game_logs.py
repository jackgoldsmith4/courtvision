from selenium.webdriver.common.action_chains import ActionChains
from utils import init_web_driver, patient_click
from selenium.webdriver.common.by import By
import pandas as pd
import time

GAMELOG_HEADER_TITLES = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc,+/-"

def scrape_game_log(player_name, rookie_year):
  driver = init_web_driver()
  driver.implicitly_wait(3)
  
  player_name = player_name.lower().split(' ')
  output_file_name = player_name[0] + '_' + player_name[1]
  # TODO: account for Miles/Mikal Bridges - they have the same ID and are labeled 01/02 in the URL
  last_name_id = player_name[1][:5] if len(player_name[1]) > 4 else player_name[1]
  player_url_id = player_name[1][0] + '/' + last_name_id + player_name[0][:2]
  url = 'https://www.basketball-reference.com/players/' + player_url_id + '01/gamelog/'

  for year in range(int(rookie_year), 2025):
    driver.get(url + str(year) + '#all_pgl_basic')
    
    # navigate to correct section
    season_header_text = str(year - 1) + '-' + str(year)[2:] + ' Regular Season'
    season_header = driver.find_element(By.XPATH, '//h2[contains(text(), "{}")]/..'.format(season_header_text))
    driver.execute_script("arguments[0].scrollIntoView(true);", season_header)
    driver.execute_script("window.scrollBy(0, -50);")

    # turn the table into CSV format #TODO not finished yet - hover/click still wip
    share_export_menu = season_header.find_element(By.CLASS_NAME, 'section_heading_text')
    actions = ActionChains(driver)
    actions.move_to_element(share_export_menu).perform()
    patient_click(driver.find_element(By.XPATH, '//*[contains(text(), "Get table as CSV")]'))
    
    # find game log elem, turn to csv table
    # if a file doesn't exist with this player's name, create one and populate with col headers and this season
    # if it does exist, just populate with this season's CSV, no headers

scrape_game_log("Stephen Curry", '2022')
