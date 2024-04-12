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

GAMELOG_HEADER_TITLES_OLD = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc"
GAMELOG_HEADER_TITLES_NEW = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc,+/-"
GAMELOG_HEADER_TITLES_DICT = "Rk,G,Date,Age,Tm,Unnamed: 5,Opp,Unnamed: 7,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc,+/-"
YEAR_TO_START = 2002
NUM_THREADS = 4

def scrape_game_log(player_url_id, rookie_year, final_year, player_name):
  url = 'https://www.basketball-reference.com/players/' + player_url_id + '/gamelog/'

  start_year = max(int(rookie_year), YEAR_TO_START)

  for year in range(start_year, int(final_year) + 1):
    # +/- is only present in gamelogs starting in 1997
    GAMELOG_HEADER_TITLES = GAMELOG_HEADER_TITLES_NEW if year >= 1997 else GAMELOG_HEADER_TITLES_OLD

    driver = init_web_driver()
    driver.implicitly_wait(5)
    driver.get(url + str(year) + '#all_pgl_basic')
    time.sleep(2)

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
      print('WARN: ' + player_name + ' ' + str(year) + ' logs not found')
      driver.quit()
      continue

    keys = GAMELOG_HEADER_TITLES_DICT.split(",")
    engine = create_engine("postgresql://bgzcpelsdernwi:b0ee04605f43866313250fad7a64d9f0299acf0d7d933e486b062a124a34085d@ec2-54-156-185-205.compute-1.amazonaws.com:5432/d5g89ferun7sda")

    for line in stats.split('\n'):
      try:
        if line == '':
          continue

        values = line.split(",")
        
        # Pairing each key with its corresponding value and creating a dictionary
        row = dict(zip(keys, values))

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
        wl, margin = row['Unnamed: 7'].split(' (')
        margin = int(margin[1:-1])
        game_outcome = 0
        if wl == 'W':
          game_outcome = margin
        else:
          game_outcome = -margin

        game_started = int(row['GS'])
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
      except ValueError as e:
        # inactive, so should show up in the box score with all zeroes
                insert_player_stat(
          engine,
          game_date=game_date,
          home_team=home_team,
          away_team=away_team,
          is_home_game=is_home_game,
          player_name=player_name,
          player_age=player_age,
          game_started=0,
          game_outcome=game_outcome,
          minutes_played=0.0,
          points=0,
          fg_made=0,
          fg_attempted=0,
          threes_made=0,
          threes_attempted=0,
          ft_made=0,
          ft_attempted=0,
          orb=0,
          drb=0,
          assists=0,
          steals=0,
          blocks=0,
          turnovers=0,
          plus_minus=0
        )

    print(f"Scraped {player_name} {year} gamelog")
    driver.quit()
    engine.dispose()

def scrape_wrapper(players):
  for index, (_, row) in enumerate(players.iterrows()):
    name = row['Name']
    br_url_id = row['Basketball-Reference URL ID']
    rookie_year = row['Rookie Year']
    final_year = row['Final Year']

    # pass over players
    if int(final_year) < YEAR_TO_START:
      continue
    
    # continually scrape until entire file has been built
    while True:
      try:
        print(f"Scraping {name} ({index}/{len(players)})")
        scrape_game_log(br_url_id, rookie_year, final_year, name)
        break
      except KeyboardInterrupt:
        raise
      except ElementNotInteractableException:
        continue
      except Exception as e:
        print(e)
        continue
  print(f"---------PROCESS COMPLETE---------")

######## SCRIPT: run scrape function on all NBA players
thread_func(NUM_THREADS, scrape_wrapper, pd.read_csv('nba_players.csv'))
