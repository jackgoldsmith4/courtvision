from utils import init_web_driver, generate_dates, heroku_print
from switching_experiment.nba_game_urls import URLS
from selenium.webdriver.common.by import By
import time

NBA_GAMES_URL = 'https://www.nba.com/games?date='

def get_nba_game_urls(dates):
  game_urls = []

  for date in dates:
    heroku_print('Scraping ' + str(date))
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
        heroku_print(f"no game details link found: {url}")

    # TODO add game URL to a Game object in the Table (recap_url field not yet created)
    with open('./nba_game_urls.py', "w") as file:
      file.write('URLS = ' + str(game_urls))
  
  return game_urls

def get_nba_game_recaps(game_urls):
  heroku_print(len(game_urls))
  for url in game_urls:
    heroku_print(url)
    driver = init_web_driver()
    driver.implicitly_wait(2)
    driver.get(url)

    # TODO add use commented out function logic (end of this file) to parse the game recap and insert into the DB
    try:
      story = driver.find_element(By.ID, 'story').text
      with open('./game_recaps/' + url.split('game/')[1] + '.txt', "w") as file:
        file.write(story)
    except:
      heroku_print(f"No recap found for {url}")
      continue

#dates = generate_dates()
#heroku_print('Getting game URLS...')
#game_urls = get_nba_game_urls(dates)
#heroku_print('Getting game recaps...')
get_nba_game_recaps(URLS[::-1])

### BELOW: logic to parse a scraped recap story
# from db.game_recaps import insert_game_recap
# from constants.team_codes import TEAM_CODES
# from sqlalchemy import create_engine
# from utils import adjust_date
# import os

# engine = create_engine("postgresql://bgzcpelsdernwi:b0ee04605f43866313250fad7a64d9f0299acf0d7d933e486b062a124a34085d@ec2-54-156-185-205.compute-1.amazonaws.com:5432/d5g89ferun7sda")

# for file_name in os.listdir('./game_recaps'):
#   try:
#     with open(f"./game_recaps/{file_name}", 'r') as file:
#       text = file.read()
    
#     name = file_name.split('-')
#     away_team = TEAM_CODES[name[0].upper()]
#     home_team = TEAM_CODES[name[2].upper()]

#     metadata, recap = text.split('\nGame Recap\n')
#     metadata = metadata.split('\n')

#     if len(metadata) >= 2:
#       headline = metadata[0]
#       game_date = adjust_date(metadata[1])
#     if len(metadata) == 3:
#       try:
#         author = metadata[2].split('By ')[1].split(' -')[0]
#       except:
#         author = None

#     insert_game_recap(engine, game_date, home_team, away_team, author.title(), headline.title(), recap)
#   except:
#     continue

# engine.dispose()
