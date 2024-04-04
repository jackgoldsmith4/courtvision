from utils import init_web_driver, generate_dates
from selenium.webdriver.common.by import By
from nba_game_urls import URLS
from dates import DATES
import time

NBA_GAMES_URL = 'https://www.nba.com/games?date='

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
