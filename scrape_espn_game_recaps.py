from utils import init_web_driver, generate_dates
from db.game_recaps import insert_game_recap
from selenium.webdriver.common.by import By
from datetime import datetime
from dates import DATES

ESPN_DATE_URL = "https://www.espn.com/nba/scoreboard/_/date/"
ESPN_RECAP_URL = "https://www.espn.com/nba/recap/_/gameId/"

def get_game_recap_urls(dates):
  urls = set()
  for date in dates:
    print(f"Scraping {date}")
    driver = init_web_driver()
    driver.get(ESPN_DATE_URL + date.replace('-', ''))
    gamecasts = driver.find_elements(By.XPATH, '//a[contains(text(), "Gamecast")]')
    for g in gamecasts:
      url_pieces = g.get_attribute('href').split('/')
      game_id = url_pieces[-2]
      if game_id != 'gameId':
        print(game_id)
        urls.add(ESPN_RECAP_URL + game_id)
    with open('./espn_game_urls.py', "w") as file:
      file.write('URLS = ' + str(list(urls)))
  
#dates = generate_dates(start_date=datetime(2002, 10, 29))
get_game_recap_urls(DATES)
