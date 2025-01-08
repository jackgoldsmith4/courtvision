from utils import init_web_driver, generate_dates, heroku_print
from db.games import add_game_recap_url, get_all_games
from selenium.webdriver.common.by import By
from constants.team_codes import TEAM_CODES
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import time
import os

NBA_GAMES_URL = 'https://www.nba.com/games?date='

def find_nba_game_recap_urls(dates):
  for date in dates:
    heroku_print('Scraping ' + date.strftime('%Y-%m-%d'))
    driver = init_web_driver(dev_headless=False)
    driver.implicitly_wait(1)
    driver.get(NBA_GAMES_URL + date.strftime('%Y-%m-%d'))
    time.sleep(1)

    game_elems = driver.find_elements(By.XPATH, '//*[contains(text(), "GAME DETAILS")]')
    for url in game_elems:
      link = url.get_attribute('href')
      if link != 'https://www.nba.com/games':
        # Connect to DB
        engine = create_engine(os.environ.get("DATABASE_URL"))
        Session = sessionmaker(bind=engine)
        session = Session()

        away_team_code, _, home_team_code, _ = link.split('/')[-1].split('-')
        add_game_recap_url(session, link, date, TEAM_CODES[home_team_code.upper()], TEAM_CODES[away_team_code.upper()])
      else:
        heroku_print(f"No game details link found: {url}")

def get_nba_game_recaps():
  engine = create_engine(os.environ.get("DATABASE_URL"))
  Session = sessionmaker(bind=engine)
  session = Session()

  games = get_all_games(session)
  for game in games:
    url = game.url
    heroku_print(url)
    driver = init_web_driver()
    driver.implicitly_wait(2)
    driver.get(url)

    try:
      story = driver.find_element(By.ID, 'story').text
      heroku_print(story)

      metadata, recap = story.split('\nGame Recap\n')
      metadata = metadata.split('\n')

      if len(metadata) >= 2:
        headline = metadata[0]
      if len(metadata) == 3:
        try:
          author = metadata[2].split('By ')[1].split(' -')[0]
        except:
          author = None
      # TODO insert recap into the Game object here
      heroku_print(author)
      heroku_print(headline)
      heroku_print(recap)
      heroku_print('---------')
    except:
      heroku_print(f"No recap found for {url}")
      driver.quit()
      continue
    driver.quit()
  session.close()
  engine.dispose()

dates = generate_dates(datetime(2019, 10, 21))
find_nba_game_recap_urls(dates)
get_nba_game_recaps()
