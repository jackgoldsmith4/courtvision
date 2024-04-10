from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from db.models import GameRecaps
from hashlib import sha256
from datetime import date

# add a new game recap to the DB
def insert_game_recap(engine, game_date, home_team, away_team, author, headline, recap_text):
  Session = sessionmaker(bind=engine)
  session = Session()
  game_id = sha256((str(game_date.date()) + home_team + away_team).encode('utf-8')).hexdigest()

  try:
    # create a new GameRecaps instance
    new_game_recap = GameRecaps(game_id=game_id, game_date=game_date.date(), home_team=home_team, away_team=away_team, author=author, headline=headline, recap_text=recap_text)

    # add the new instance to the session and commit it to the database
    session.add(new_game_recap)
    session.commit()
    print(f"New game recap successfully added: {away_team} @ {home_team} ({game_date})\nHeadline: {headline}")
  except IntegrityError:
    print("Duplicate game recap found")
  except Exception as e:
    session.rollback()
    print(f"Failed to add game recap. Error: {e}")
    session.close()
    return 500
  finally:
    session.close()
    return 200

# get a game recap headline by ID
def get_game_recap_headline(engine, game_date, home_team, away_team):
  Session = sessionmaker(bind=engine)
  session = Session()
  stmt = select(GameRecaps).filter_by(home_team=home_team, away_team=away_team, game_date=game_date)
  game_recap = session.execute(stmt).first()

  session.close()
  return game_recap[0].headline

def get_game_recaps(engine, n=3):
  Session = sessionmaker(bind=engine)
  session = Session()
  stmt = select(GameRecaps).order_by(func.random()).limit(n)
  game_recaps = session.execute(stmt).scalars().all()

  session.close()
  return [r.__dict__.items() for r in game_recaps]
