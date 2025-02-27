from utils import init_web_driver, patient_click, convert_time_to_float, heroku_print
from selenium.webdriver.common.action_chains import ActionChains
from db.player_game_logs import insert_player_game_log
from db.players import get_players, insert_player
from selenium.webdriver.common.by import By
from constants.team_codes import TEAM_CODES
from db.games import insert_game
from datetime import datetime
from db.db import get_session
import time
import os

GAMELOG_HEADER_TITLES_OLD = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc"
GAMELOG_HEADER_TITLES_NEW = "Rk,G,Date,Age,Tm,,Opp,,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc,+/-"
GAMELOG_HEADER_TITLES_DICT = "Rk,G,Date,Age,Tm,Unnamed: 5,Opp,Unnamed: 7,GS,MP,FG,FGA,FG%,3P,3PA,3P%,FT,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GmSc,+/-"
YEAR_TO_START = 1997
YEAR_TO_END = 2018
NUM_THREADS = int(os.environ.get("NUM_THREADS"))

def scrape_game_log(player_id, player_name, rookie_year, final_year):
  url = 'https://www.basketball-reference.com/players/' + player_id + '/gamelog/'
  start_year = max(int(rookie_year), YEAR_TO_START)

  year = start_year
  while year <= int(final_year):
    try:
      heroku_print(f"Scraping {player_name}'s {year} gamelog")

      # +/- is only present in gamelogs starting in 1997
      GAMELOG_HEADER_TITLES = GAMELOG_HEADER_TITLES_NEW if year >= 1997 else GAMELOG_HEADER_TITLES_OLD

      driver = init_web_driver()
      driver.implicitly_wait(5)
      url_with_year = f"{url}{year}#all_pgl_basic"

      timeout_duration = 10
      driver.set_page_load_timeout(timeout_duration)

      # if the page load times out, try again
      driver.get(url_with_year)
      time.sleep(2)

      # turn the table into CSV format and grab stats
      season_header_text = str(year - 1) + '-' + str(year)[2:] + ' Regular Season'
      try:
        season_header = driver.find_element(By.XPATH, '//h2[contains(text(), "{}")]/..'.format(season_header_text))
      except:
        heroku_print(f"WARN: season headers not found for {player_name} in {year}")
        # player did not play this year
        year += 1
        driver.quit()
        continue
      share_export_menu = season_header.find_element(By.CLASS_NAME, 'section_heading_text')
      actions = ActionChains(driver)
      actions.move_to_element(share_export_menu).perform()
      patient_click(driver.find_element(By.XPATH, '//*[contains(text(), "Get table as CSV")]'))
      try:
        stats = driver.find_element(By.TAG_NAME, 'pre').text.split(GAMELOG_HEADER_TITLES)[1]
      except:
        heroku_print(f"WARN: {player_name} {year} logs not found")
        # player did not play this year
        year += 1
        driver.quit()
        continue

      driver.quit()
      keys = GAMELOG_HEADER_TITLES_DICT.split(",")
      with get_session() as session:
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

            # get/create Player and Game objects
            game = insert_game(session, game_date, home_team, away_team)
            player = insert_player(session, player_id, player_name, rookie_year, final_year)

            game_started = int(row['GS'])
            try:
              plus_minus=int(row['+/-'])
            except ValueError:
              plus_minus=0

            insert_player_game_log(
              session,
              game=game,
              player=player,
              is_home_game=is_home_game,
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
            # player was inactive for this game, so should show up in the box score with all zeroes
            insert_player_game_log(
              session,
              game=game,
              player=player,
              is_home_game=is_home_game,
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
        heroku_print(f"Scraped {player_name}'s {year} gamelog")
        year += 1
    except Exception as e:
      heroku_print(f"Error scraping: {e}")
      continue

######## SCRIPT: run scrape function on all NBA players
with get_session() as session:
  players = get_players(session, after_year=YEAR_TO_START)
  for index, player in enumerate(players):
    player_name = player['name']
    heroku_print(f"Scraping {player_name} ({index}/{len(players)})")
    scrape_game_log(player['id'], player_name, player['start_year'], min(YEAR_TO_END, player['end_year']))
