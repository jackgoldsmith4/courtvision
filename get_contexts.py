from db.player_stats import get_flattened_player_stats_by_game_id
from db.game_recaps import get_game_recaps
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pandas as pd

def get_contexts():
  engine = create_engine("postgresql://bgzcpelsdernwi:b0ee04605f43866313250fad7a64d9f0299acf0d7d933e486b062a124a34085d@ec2-54-156-185-205.compute-1.amazonaws.com:5432/d5g89ferun7sda")

  recaps = get_game_recaps(engine, n=40000)
  contexts_df = pd.DataFrame(columns=['headline', 'context'])

  for index, r in enumerate(recaps):
    print(f"Recap {index}/{len(recaps)}")
    r_dict = dict(r)
    home_team = r_dict['home_team']
    away_team = r_dict['away_team']
    headline = r_dict['headline']
    game_date = r_dict['game_date']
    
    try:
      Session = sessionmaker(bind=engine)
      session = Session()
      context = get_flattened_player_stats_by_game_id(session, game_date, home_team, away_team)
      session.close()
    except ValueError:
      print("ValueError")
      session.close()
      continue
    
    if context.count('player_name:') > 10:
      contexts_df.loc[len(contexts_df)] = (headline, context)

  contexts_df.to_csv('./contexts.csv', index=False)
  engine.dispose()

get_contexts()
