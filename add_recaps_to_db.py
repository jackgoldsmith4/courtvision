from db.game_recaps import insert_game_recap
from constants.team_codes import TEAM_CODES
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import os
import re

# adjust date based on the date string in the game recap
def adjust_date(date_str):
  date_str = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_str)
  dt = datetime.strptime(date_str, '%A, %B %d, %Y %I:%M %p')
  if "AM" in date_str and dt.hour < 12:
    dt = dt - timedelta(days=1)
  return dt.date()

engine = create_engine("postgresql://bgzcpelsdernwi:b0ee04605f43866313250fad7a64d9f0299acf0d7d933e486b062a124a34085d@ec2-54-156-185-205.compute-1.amazonaws.com:5432/d5g89ferun7sda")

for file_name in os.listdir('./game_recaps'):
  try:
    with open(f"./game_recaps/{file_name}", 'r') as file:
      text = file.read()
    
    name = file_name.split('-')
    away_team = TEAM_CODES[name[0].upper()]
    home_team = TEAM_CODES[name[2].upper()]

    metadata, recap = text.split('\nGame Recap\n')
    metadata = metadata.split('\n')

    if len(metadata) >= 2:
      headline = metadata[0]
      game_date = adjust_date(metadata[1])
    if len(metadata) == 3:
      try:
        author = metadata[2].split('By ')[1].split(' -')[0]
      except:
        author = None

    insert_game_recap(engine, game_date, home_team, away_team, author.title(), headline.title(), recap)
  except:
    continue

engine.dispose()
