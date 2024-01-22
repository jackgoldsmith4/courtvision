from selenium.webdriver.common.action_chains import ActionChains
from utils import init_web_driver, patient_click
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

GAMELOG_HEADER_TITLES = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc,+/-"

def scrape_game_log(player_name, rookie_year, player_url_id):
  driver = init_web_driver()
  driver.implicitly_wait(3)
  
  player_name = player_name.lower().split(' ')
  output_file_name = player_name[0] + '_' + player_name[1] + '.csv'
  output_file_path = './player_game_logs/' + output_file_name
  url = 'https://www.basketball-reference.com/players/' + player_url_id + '/gamelog/'

  for year in range(int(rookie_year), 2025):
    # check if this year and player have already been read (always read current season for newest games)
    gamelog_filenames = os.listdir('./player_game_logs')
    if output_file_name in gamelog_filenames:
      with open(output_file_path, 'rb') as file:
        file.seek(-2, os.SEEK_END)  # Go to the second last byte in the file
        while file.read(1) != b'\n':  # Keep stepping back until you find the newline
          file.seek(-2, os.SEEK_CUR)
        most_recent_year_in_file = int(file.readline().decode().split(',')[2].split('-')[0])
        if most_recent_year_in_file >= year: # TODO add (and year != 2024) once df stuff is fixed below
          continue

    print('Building ' + output_file_name + ' (' + str(year) + ' gamelog)...')
    driver.get(url + str(year) + '#all_pgl_basic')
    time.sleep(3)

    # turn the table into CSV format and grab stats
    season_header_text = str(year - 1) + '-' + str(year)[2:] + ' Regular Season'
    try:
      season_header = driver.find_element(By.XPATH, '//h2[contains(text(), "{}")]/..'.format(season_header_text))
    except:
      print('WARN: ' + output_file_name + ' ' + str(year) + ' logs not found')
      continue
    share_export_menu = season_header.find_element(By.CLASS_NAME, 'section_heading_text')
    actions = ActionChains(driver)
    actions.move_to_element(share_export_menu).perform()
    patient_click(driver.find_element(By.XPATH, '//*[contains(text(), "Get table as CSV")]'))
    stats = driver.find_element(By.TAG_NAME, 'pre').text.split(GAMELOG_HEADER_TITLES)[1]

    # if a file doesn't exist with this player's name, create one and populate with col headers and this season
    if output_file_name not in gamelog_filenames:
      with open(output_file_path, 'w') as file:
        file.write(GAMELOG_HEADER_TITLES)
        file.write(stats)
    else:
      with open(output_file_path, 'a') as file:
        file.write(stats)

    # # drop duplicate games for current season
    # # TODO need to also name cols (home/away) and drop stuff (e.g. game/rk #) here
    # if year == 2024:
    #   df = pd.read_csv(output_file_path)
    #   df.drop_duplicates(inplace=True)
    #   df.to_csv(output_file_path, index=False)

active_players = pd.read_csv('active_players.csv')
for index, row in active_players.iterrows():
  name = row['Name']
  rookie_year = row['Rookie Year']
  br_url_id = row['Basketball-Reference URL ID']

  # continually scrape until entire file has been built
  while True:
    try:
      scrape_game_log(name, rookie_year, br_url_id)
      break
    except KeyboardInterrupt:
      raise
    except Exception as e:
      print(e)
      continue
