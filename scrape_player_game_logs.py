from utils import init_web_driver, patient_click, thread_func, convert_time_to_float
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from db.player_stats import insert_player_stat
from selenium.webdriver.common.by import By
from constants.team_codes import TEAM_CODES
from sqlalchemy import create_engine
from datetime import datetime
import pandas as pd
import time
import os

GAMELOG_HEADER_TITLES_OLD = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc"
GAMELOG_HEADER_TITLES_NEW = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc,+/-"
NUM_THREADS = 40

def scrape_game_log(player_url_id, rookie_year, final_year, player_name, output_file_path, only_scrape_actives):
  url = 'https://www.basketball-reference.com/players/' + player_url_id + '/gamelog/'
  were_games_scraped = False

  # find year to start
  start_year = int(rookie_year)
  gamelog_filenames = os.listdir('./player_game_logs')
  if player_name in gamelog_filenames:
    with open(output_file_path, 'rb') as file:
      file.seek(-2, os.SEEK_END)  # go to the second last byte in the file
      while file.read(1) != b'\n':  # keep stepping back until you find the newline
        file.seek(-2, os.SEEK_CUR)
      most_recent_year_in_file, most_recent_month_in_file = file.readline().decode().split(',')[2].split('-')[0:2]
    # start from most recent season
    start_year = int(most_recent_year_in_file) + 1 if int(most_recent_month_in_file) < 10 else int(most_recent_year_in_file) + 2
    # catch most recent season for active players no matter what
    if only_scrape_actives and start_year > 2024:
      start_year = 2024

  for year in range(start_year, int(final_year) + 1):
    # +/- is only present in gamelogs starting in 1997
    GAMELOG_HEADER_TITLES = GAMELOG_HEADER_TITLES_NEW if year >= 1997 else GAMELOG_HEADER_TITLES_OLD

    driver = init_web_driver()
    driver.implicitly_wait(5)
    driver.get(url + str(year) + '#all_pgl_basic')
    time.sleep(3)

    # turn the table into CSV format and grab stats
    season_header_text = str(year - 1) + '-' + str(year)[2:] + ' Regular Season'
    try:
      season_header = driver.find_element(By.XPATH, '//h2[contains(text(), "{}")]/..'.format(season_header_text))
    except:
      driver.quit()
      continue
    share_export_menu = season_header.find_element(By.CLASS_NAME, 'section_heading_text')
    actions = ActionChains(driver)
    actions.move_to_element(share_export_menu).perform()
    patient_click(driver.find_element(By.XPATH, '//*[contains(text(), "Get table as CSV")]'))
    try:
      stats = driver.find_element(By.TAG_NAME, 'pre').text.split(GAMELOG_HEADER_TITLES)[1]
    except:
      print('WARN: ' + player_name + ' ' + str(year) + ' logs not found DUE TO GAMELOG COLS')
      driver.quit()
      continue

    # # write or append to the player's gamelog file
    # if player_name not in gamelog_filenames and not were_games_scraped:
    #   with open(output_file_path, 'w') as file:
    #     # always include new titles to get +/- as a column
    #     file.write(GAMELOG_HEADER_TITLES_NEW)
    #     file.write(stats)
    # else:
    #   with open(output_file_path, 'a') as file:
    #     file.write(stats)

    keys = GAMELOG_HEADER_TITLES_NEW.split(",")
    engine = create_engine("postgresql://bgzcpelsdernwi:b0ee04605f43866313250fad7a64d9f0299acf0d7d933e486b062a124a34085d@ec2-54-156-185-205.compute-1.amazonaws.com:5432/d5g89ferun7sda")

    for line in stats.split('\n'):
      values = line.split(",")

      # Pairing each key with its corresponding value and creating a dictionary
      row = dict(zip(keys, values))

      try:
        game_date = datetime.strptime(row['Date'], "%Y-%m-%d").date()

        is_home_game = 1
        if row['Unnamed: 5'] == '@':
          is_home_game = 0

        home_team = ''
        away_team = ''
        if is_home_game == 1:
          home_team = TEAM_CODES[row['Tm']]
          away_team = TEAM_CODES[row['Opp']]
        else:
          home_team = TEAM_CODES[row['Opp']]
          away_team = TEAM_CODES[row['Tm']]
        
        years, days = row['Age'].split('-')
        player_age = 365*int(years) + int(days)
        game_started = int(row['GS'])
        wl, margin = row['Unnamed: 7'].split(' (')
        margin = int(margin[1:-1])
        game_outcome = 0
        if wl == 'W':
          game_outcome = margin
        else:
          game_outcome = -margin

        try:
          plus_minus=int(row['+/-'])
        except ValueError:
          plus_minus=0

        insert_player_stat(
          engine,
          game_date=game_date,
          home_team=home_team,
          away_team=away_team,
          is_home_game=is_home_game,
          player_name=player_name,
          player_age=player_age,
          game_started=game_started,
          game_outcome=game_outcome,
          minutes_played=convert_time_to_float(row['MP']),
          points=int(row['PTS']),
          fg_made=int(row['FG']),
          fg_attempted=int(row['FGA']),
          threes_made=int(row['3P']),
          threes_attempted=int(row['3PA']),
          ft_made=int(row['FT']),
          ft_attempted=int(row['FTA']),
          orb=int(row['ORB']),
          drb=int(row['DRB']),
          assists=int(row['AST']),
          steals=int(row['STL']),
          blocks=int(row['BLK']),
          turnovers=int(row['TOV']),
          plus_minus=plus_minus
        )
      except:
        raise

    were_games_scraped = True
    print(f"Scraped {player_name} {year} gamelog")
    driver.quit()
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

    # pass over players
    if (int(final_year) - int(rookie_year) >= 3) or (int(rookie_year) < 2001):
      continue

    player_name = '_'.join(name.lower().replace('.', '').split(' '))
    subdir_path = './player_game_logs/' + player_name
    # Create the subdirectory
    if not os.path.exists(subdir_path):
      os.makedirs(subdir_path)
    output_file_path = subdir_path + player_name + '_RAW.csv'
    were_games_scraped = False

    # continually scrape until entire file has been built
    while True:
      try:
        were_games_scraped = scrape_game_log(br_url_id, rookie_year, final_year, player_name, output_file_path, only_scrape_actives)
        break
      except KeyboardInterrupt:
        raise
      except ElementNotInteractableException:
        continue
      except Exception as e:
        print(player_name)
        print(e)
        continue
    
    # # after reading, clean the data if any games were scraped
    # if were_games_scraped:
    #   player_df = pd.read_csv(output_file_path)

    #   # drop duplicate games in case games were scraped more than once
    #   player_df.drop_duplicates(inplace=True)

    #   # drop rows in which player didn't play
    #   player_df = player_df.dropna(subset=['G'])
    #   player_df = player_df.astype({'G': 'int32'})

    #   player_df.to_csv(output_file_path, index=False)
  print(f"---------PROCESS COMPLETE---------")

######## SCRIPT: run scrape function on all NBA players
thread_func(NUM_THREADS, scrape_wrapper, pd.read_csv('nba_players.csv'))
