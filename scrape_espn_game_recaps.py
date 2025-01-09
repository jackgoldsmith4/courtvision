from utils import init_web_driver, generate_dates, heroku_print
from selenium.webdriver.common.by import By
from db.games import add_game_recap_to_game
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import traceback
import time
import os

ESPN_DATE_URL = "https://www.espn.com/nba/scoreboard/_/date/"
ESPN_RECAP_URL = "https://www.espn.com/nba/recap/_/gameId/"

def clean_espn_team_name(team_name):
  if team_name == 'Clippers':
    team_name = 'Los Angeles Clippers'
  if team_name == '76ers':
    team_name = 'Philadelphia 76ers'
  team_name = team_name.replace('LA Clippers', 'Los Angeles Clippers')
  return team_name

def find_espn_game_recaps(dates):
  engine = create_engine(os.environ.get("DATABASE_URL"))
  Session = sessionmaker(bind=engine)
  session = Session()

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
            if flag == 1:
              home_team = t.text
              break
            text = t.text
            if len(text) > 3 and text.title() == text:
              away_team = text
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
  session.close()
  engine.dispose()

# SCRIPT
dates = generate_dates(start_date=datetime(2012, 10, 31).date())
find_espn_game_recaps(dates)
