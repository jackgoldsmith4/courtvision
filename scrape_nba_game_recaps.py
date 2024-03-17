from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from utils import init_web_driver
from nba_game_urls import URLS
from dates import DATES
import time

NBA_GAMES_URL = 'https://www.nba.com/games?date='

def generate_dates(start_date=datetime(2019, 10, 1)):
  end_date = datetime.now()
  delta = end_date - start_date
  date_list = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
  date_strs = [date.strftime('%Y-%m-%d') for date in date_list]

  with open('./dates.py', "w") as file:
    file.write('DATES = ' + str(date_strs))
  return date_strs

def get_nba_game_urls(dates):
  game_urls = []

  for date in dates:
    print('Scraping ' + str(date))
    driver = init_web_driver()
    driver.implicitly_wait(1)
    driver.get(NBA_GAMES_URL + date)
    time.sleep(1)

    game_elems = driver.find_elements(By.XPATH, '//*[contains(text(), "GAME DETAILS")]')
    for url in game_elems:
      game_urls.append(url.get_attribute('href'))
    
    with open('./nba_game_urls.py', "w") as file:
      file.write('URLS = ' + str(game_urls))

def get_nba_game_recaps(game_urls):
  for url in game_urls:
    print(url)
    driver = init_web_driver()
    driver.implicitly_wait(2)
    driver.get(url)

    try:
      story = driver.find_element(By.ID, 'story').text
      with open('./game_recaps/' + url.split('game/')[1] + '.txt', "w") as file:
        file.write(story)
    except:
      print('not gonna happen')
      continue

#dates = generate_dates()
#get_nba_game_urls(DATES)
get_nba_game_recaps(URLS)
