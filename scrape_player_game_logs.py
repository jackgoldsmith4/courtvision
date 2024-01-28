from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from utils import init_web_driver, patient_click
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import threading
import time
import os

GAMELOG_HEADER_TITLES_OLD = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc"
GAMELOG_HEADER_TITLES_NEW = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc,+/-"
NUM_THREADS = 4

def scrape_game_log(player_url_id, rookie_year, final_year, output_file_name, output_file_path):
  driver = init_web_driver()
  driver.implicitly_wait(5)

  url = 'https://www.basketball-reference.com/players/' + player_url_id + '/gamelog/'
  were_games_scraped = False

  # find year to start
  start_year = int(rookie_year)
  gamelog_filenames = os.listdir('./player_game_logs')
  if output_file_name in gamelog_filenames:
    with open(output_file_path, 'rb') as file:
      file.seek(-2, os.SEEK_END)  # go to the second last byte in the file
      while file.read(1) != b'\n':  # keep stepping back until you find the newline
        file.seek(-2, os.SEEK_CUR)
      most_recent_year_in_file = int(file.readline().decode().split(',')[2].split('-')[0])
      most_recent_month_in_file = int(file.readline().decode().split(',')[2].split('-')[0])
    # start from most recent season
    # (some overlap may occur with most recent season in previous file version, so dupes dropped later)
    start_year = most_recent_year_in_file + 1 if most_recent_year_in_file < 2024 else 2024
    # skip players whos last season isn't in the final year (no new games to scrape)
    if start_year == final_year and most_recent_month_in_file > 9:
      return were_games_scraped

  for year in range(start_year, int(final_year) + 1):
    # +/- is only present in gamelogs starting in 1997
    GAMELOG_HEADER_TITLES = GAMELOG_HEADER_TITLES_NEW if year >= 1997 else GAMELOG_HEADER_TITLES_OLD

    driver.get(url + str(year) + '#all_pgl_basic')
    time.sleep(3)

    # turn the table into CSV format and grab stats
    season_header_text = str(year - 1) + '-' + str(year)[2:] + ' Regular Season'
    try:
      season_header = driver.find_element(By.XPATH, '//h2[contains(text(), "{}")]/..'.format(season_header_text))
    except:
      continue
    share_export_menu = season_header.find_element(By.CLASS_NAME, 'section_heading_text')
    actions = ActionChains(driver)
    actions.move_to_element(share_export_menu).perform()
    patient_click(driver.find_element(By.XPATH, '//*[contains(text(), "Get table as CSV")]'))
    try:
      stats = driver.find_element(By.TAG_NAME, 'pre').text.split(GAMELOG_HEADER_TITLES)[1]
    except Exception:
      print('WARN: ' + output_file_name + ' ' + str(year) + ' logs not found DUE TO GAMELOG COLS')
      continue     

    # write or append to the player's gamelog file
    if output_file_name not in gamelog_filenames and not were_games_scraped:
      with open(output_file_path, 'w') as file:
        # always include new titles to get +/- as a column
        file.write(GAMELOG_HEADER_TITLES_NEW)
        file.write(stats)
    else:
      with open(output_file_path, 'a') as file:
        file.write(stats)
    were_games_scraped = True
    print(f"Scraped {output_file_name} {year} gamelog")
  return were_games_scraped

def scrape_wrapper(players, only_scrape_actives=False):
  for _, row in players.iterrows():
    name = row['Name']
    br_url_id = row['Basketball-Reference URL ID']
    rookie_year = row['Rookie Year']
    final_year = row['Final Year']

    # skip retired players if flag is set
    if only_scrape_actives and final_year != 2024:
      continue

    # pass over players who have played in two or fewer seasons, or who played before 1980 (when 3PT began)
    if (int(final_year) - int(rookie_year) < 2) or (int(rookie_year) < 1980):
      continue

    player_name = name.lower().replace('.', '').split(' ')
    output_file_name = '_'.join(player_name) + '.csv'
    output_file_path = './player_game_logs/' + output_file_name
    were_games_scraped = False

    # continually scrape until entire file has been built
    while True:
      try:
        were_games_scraped = scrape_game_log(br_url_id, rookie_year, final_year, output_file_name, output_file_path)
        break
      except KeyboardInterrupt:
        raise
      except ElementNotInteractableException:
        continue
      except Exception as e:
        print(e)
        continue
    
    # after reading, clean the data if any games were scraped
    if were_games_scraped:
      player_df = pd.read_csv(output_file_path)

      # drop duplicate games in case games were scraped more than once
      player_df.drop_duplicates(inplace=True)

      # drop rows in which player didn't play
      player_df = player_df.dropna(subset=['G'])
      player_df = player_df.astype({'G': 'int32'})

      # output back to CSV
      player_df.to_csv(output_file_path, index=False)

######## SCRIPT: run scrape function on all NBA players
players = pd.read_csv('nba_players.csv')
players_split = np.array_split(players, NUM_THREADS)

threads = []
for i in range(NUM_THREADS):
  thread = threading.Thread(target=scrape_wrapper, args=(players_split[i],))
  threads.append(thread)

for thread in threads:
  thread.start()
for thread in threads:
  thread.join()
