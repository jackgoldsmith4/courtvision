from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from utils import init_web_driver
from nba_game_urls import URLS
from dates import DATES
import time

NBA_GAMES_URL = 'https://www.nba.com/games?date='

def generate_dates(start_date=datetime(2005, 10, 1)):
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
      link = url.get_attribute('href')
      if link != 'https://www.nba.com/games':
        game_urls.append(link)
      else:
        print(f"no game details link found: {url}")
    
    with open('./nba_game_urls.py', "w") as file:
      file.write('URLS = ' + str(game_urls))
  
  return game_urls

def get_nba_game_recaps(game_urls):
  print(len(game_urls))
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
      print(f"no recap found for {url}")
      continue

#dates = generate_dates()
#print('Getting game URLS...')
#game_urls = get_nba_game_urls(DATES)
#print('Getting game recaps...')
get_nba_game_recaps(URLS[::-1])
