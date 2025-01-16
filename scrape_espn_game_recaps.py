from utils import init_web_driver, generate_dates, heroku_print
from selenium.webdriver.common.by import By
from db.games import add_game_recap_to_game
from datetime import datetime
from db.db import get_session
import traceback
import time

ESPN_DATE_URL = "https://www.espn.com/nba/scoreboard/_/date/"
ESPN_RECAP_URL = "https://www.espn.com/nba/recap/_/gameId/"

def clean_espn_team_name(team_name):
  team_name = team_name.replace('LA Clippers', 'Los Angeles Clippers')
  return team_name

def find_espn_game_recaps(dates):
  with get_session() as session:
    for date in dates:
      try:
        heroku_print(f"Scraping {date}")
        driver = init_web_driver()
        driver.get(ESPN_DATE_URL + date.strftime('%Y%m%d').replace('-', ''))
        gamecasts = driver.find_elements(By.XPATH, '//a[contains(text(), "Gamecast")]')
        urls = []
        for g in gamecasts:
          url_pieces = g.get_attribute('href').split('/')
          game_id = url_pieces[-2]
          if game_id != 'gameId':
            url = ESPN_RECAP_URL + game_id
            urls.append(url)
        driver.quit()

        for recap_url in urls:
          driver = init_web_driver()
          driver.get(recap_url)
          time.sleep(1)

          try:
            headline = driver.find_element(By.CLASS_NAME, 'Story__Headline').text
            author = driver.find_element(By.CLASS_NAME, 'Byline__Author').text
            recap_text = driver.find_element(By.CLASS_NAME, 'Story__Body').text
            teams = driver.find_elements(By.CLASS_NAME, 'ScoreCell__TeamName')

            # isolate home and away team names
            home_team = ''
            away_team = ''
            flag = 0
            for t in teams:
              team_name = t.text
              if flag == 1:
                home_team = team_name
                break
              if len(team_name) > 3:
                away_team = team_name
                flag = 1
          except:
            driver.quit()
            continue
          driver.quit()

          away_team = clean_espn_team_name(away_team)
          home_team = clean_espn_team_name(home_team)

          add_game_recap_to_game(session, recap_url, headline, author, recap_text, date, home_team, away_team)
      except:
        heroku_print(f"An Error Occurred: {traceback.format_exc()}")
        driver.quit()
        continue

# SCRIPT
dates = generate_dates(start_date=datetime(2012, 11, 7).date())
find_espn_game_recaps(dates)
