from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from db.models import GameRecaps
from hashlib import sha256

# add a new game recap to the DB
def insert_game_recap(engine, game_date, home_team, away_team, author, headline, recap_text):
  Session = sessionmaker(bind=engine)
  session = Session()
  game_id = sha256((str(game_date) + home_team + away_team).encode('utf-8')).hexdigest()

  try:
    # create a new GameRecaps instance
    new_game_recap = GameRecaps(game_id=game_id, game_date=game_date, home_team=home_team, away_team=away_team, author=author, headline=headline, recap_text=recap_text)

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
  Session = sessionmaker(bind=engine)
  session = Session()
  stmt = select(GameRecaps).filter_by(game_id=game_id)
  game_recap = session.execute(stmt).first()

  session.close()
  return game_recap

def get_game_recaps(engine, n=3):
  Session = sessionmaker(bind=engine)
  session = Session()
  stmt = select(GameRecaps).order_by(func.random()).limit(n)
  game_recaps = session.execute(stmt).scalars().all()

  session.close()
  return [r.__dict__.items() for r in game_recaps]
