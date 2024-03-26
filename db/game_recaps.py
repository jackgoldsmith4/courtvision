from sqlalchemy.orm import sessionmaker
from models import GameRecaps
from hashlib import sha256

# add a new game recap to the DB
def insert_game_recap(engine, game_date, home_team, away_team, author, recap_text):
  session = sessionmaker(bind=engine)
  game_id = sha256(str(game_date) + home_team + away_team)

  try:
    # create a new GameRecaps instance
    new_game_recap = GameRecaps(game_id=game_id, game_date=game_date, home_team=home_team, away_team=away_team, author=author, recap_text=recap_text)

    # add the new instance to the session and commit it to the database
    session.add(new_game_recap)
    session.commit()
    print("New game recap successfully added.")
  except Exception as e:
    session.rollback()
    print(f"Failed to add game recap. Error: {e}")
  finally:
    session.close()

# get a game recap by ID
def get_game_recap(engine, game_id):
  session = sessionmaker(bind=engine)
  game_recap = session.query(GameRecaps).filter_by(game_id=game_id).first()
  return game_recap
