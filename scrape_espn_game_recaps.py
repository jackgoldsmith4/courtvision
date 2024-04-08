from utils import init_web_driver, generate_dates, adjust_date, thread_func
from db.game_recaps import insert_game_recap
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from espn_game_urls import URLS
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
      game_date = driver.find_element(By.CLASS_NAME, 'Byline__Meta--publishDate').text
      recap = driver.find_element(By.CLASS_NAME, 'Story__Body').text
      teams = driver.find_elements(By.CLASS_NAME, 'ScoreCell__TeamName')

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
    except Exception as e:
      print(e)
      driver.quit()
      continue
    
    driver.quit()
    if 'Updated: ' in game_date:
      game_date = game_date.split('Updated: ')[1]
    
    try:
      game_date = game_date.split(', ')
      game_date = create_date_object(game_date)
    except:
      continue

    insert_game_recap(engine, game_date, home_team, away_team, None, headline, recap)
  engine.dispose()

def create_date_object(date_parts):
  # Parse the date and time components
  date_str = f"{date_parts[0]} {date_parts[1]} {date_parts[2]}"
  date_format = "%b %d %Y %I:%M %p"
  
  # Convert to datetime object
  date_obj = datetime.strptime(date_str, date_format)
  
  # Check for "am" and adjust the date accordingly
  if "am" in date_parts[2]:
    date_obj -= timedelta(days=1)
      
  return date_obj
  
#dates = generate_dates(start_date=datetime(2016, 1, 14))
#get_game_recap_urls(dates)

thread_func(4, get_espn_game_recaps, URLS)
