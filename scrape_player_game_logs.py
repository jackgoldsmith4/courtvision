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
  for year in range(int(rookie_year), int(final_year) + 1):
    # +/- is only present in gamelogs starting in 1997
    GAMELOG_HEADER_TITLES = GAMELOG_HEADER_TITLES_NEW if year >= 1997 else GAMELOG_HEADER_TITLES_OLD

    # check if this year and player have already been read (always read current season for newest games)
    gamelog_filenames = os.listdir('./player_game_logs')
    if output_file_name in gamelog_filenames:
      with open(output_file_path, 'rb') as file:
        file.seek(-2, os.SEEK_END)  # Go to the second last byte in the file
        while file.read(1) != b'\n':  # Keep stepping back until you find the newline
          file.seek(-2, os.SEEK_CUR)
        most_recent_year_in_file, most_recent_month_in_file = file.readline().decode().split(',')[2].split('-')[0:2]
        if int(most_recent_year_in_file) >= year: # and year != 2024: TODO cant add new 2024 games in old format once cleaned
          continue
        elif int(most_recent_year_in_file) == year - 1 and int(most_recent_month_in_file) > 9:
          # this means the player played this specific season, but not this specific year
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
    try:
      stats = driver.find_element(By.TAG_NAME, 'pre').text.split(GAMELOG_HEADER_TITLES)[1]
    except:
      print('WARN: ' + output_file_name + ' ' + str(year) + ' logs not found DUE TO GAMELOG COLS')
      continue     

    # write or append to the player's gamelog file
    were_games_scraped = True
    if output_file_name not in gamelog_filenames:
      with open(output_file_path, 'w') as file:
        # always include new titles to get +/- as a column
        file.write(GAMELOG_HEADER_TITLES_NEW)
        file.write(stats)
    else:
      with open(output_file_path, 'a') as file:
        file.write(stats)
  return were_games_scraped

def scrape_wrapper(players):
  for _, row in players.iterrows():
    name = row['Name']
    br_url_id = row['Basketball-Reference URL ID']
    rookie_year = row['Rookie Year']
    final_year = row['Final Year']

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
      except Exception as e:
        print(e)
        continue
    
    # after reading, clean the data if any games were scraped
    if were_games_scraped:
      player_df = pd.read_csv(output_file_path)

      # drop duplicate games for current season
      if final_year == 2024:
        player_df.drop_duplicates(inplace=True)

      # rename some cols for clarity
      player_df.rename(columns={
        'Unnamed: 5': 'Home/Away',
        'Unnamed: 7': 'Win/Loss',
        'Rk': 'Game of season',
        'G': 'Game for player',
        'Tm': 'Team',
        'Age': 'Age (days)'
      }, inplace=True)

      # cleanup some of the columns
      player_df['Home/Away'].fillna('H', inplace=True)
      player_df['Home/Away'].replace('@','A', inplace=True)
      player_df['Date'] = pd.to_datetime(player_df['Date'])

      # convert age to days
      try:
        years, days = player_df['Age (days)'].str.split('-', expand=True).astype(int).values.T
        player_df['Age (days)'] = player_df['Age (days)'] = years * 365 + days
      except:
        print(player_name)
        print('-------')
        raise

      # drop rows in which player didn't play
      player_df = player_df.dropna(subset=['Game for player'])
      player_df = player_df.astype({'Game for player': 'int32'})

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
