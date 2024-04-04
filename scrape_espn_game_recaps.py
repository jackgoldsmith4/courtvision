from utils import init_web_driver, generate_dates, adjust_date
from db.game_recaps import insert_game_recap
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine
from datetime import datetime
from dates import DATES

ESPN_DATE_URL = "https://www.espn.com/nba/scoreboard/_/date/"
ESPN_RECAP_URL = "https://www.espn.com/nba/recap/_/gameId/"

def get_game_recap_urls(dates):
  urls = set()
  for date in dates:
    try:
      print(f"Scraping {date}")
      driver = init_web_driver()
      driver.get(ESPN_DATE_URL + date.replace('-', ''))
      gamecasts = driver.find_elements(By.XPATH, '//a[contains(text(), "Gamecast")]')
      for g in gamecasts:
        url_pieces = g.get_attribute('href').split('/')
        game_id = url_pieces[-2]
        if game_id != 'gameId':
          urls.add(ESPN_RECAP_URL + game_id)
      with open('./espn_game_urls_3.py', "w") as file:
        file.write('URLS = ' + str(list(urls)))
    except Exception as e:
      print(e)
      continue

def get_espn_game_recaps(urls):
  engine = create_engine("postgresql://bgzcpelsdernwi:b0ee04605f43866313250fad7a64d9f0299acf0d7d933e486b062a124a34085d@ec2-54-156-185-205.compute-1.amazonaws.com:5432/d5g89ferun7sda")
  for url in urls:
    driver = init_web_driver()
    driver.get(url)

    try:
      headline = driver.find_element(By.CLASS_NAME, 'Story__Headline').text
      game_date = driver.find_element(By.XPATH, '//*[contains(text(), "Updated: ")]').text.split('Updated: ')[1]
      recap = driver.find_element(By.CLASS_NAME, 'Story__Body').text
      # TODO get home and away teams
      home_team = ''
      away_team = ''
    except:
      continue

    # TODO new adjust_date func for getting correct game_date Date object

    insert_game_recap(engine, game_date, home_team, away_team, None, headline, recap)
  
dates = generate_dates(start_date=datetime(2016, 1, 14))
get_game_recap_urls(dates)
