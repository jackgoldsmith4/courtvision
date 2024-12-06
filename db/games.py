from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from db.models import Game
from hashlib import sha256
from datetime import date
import traceback

def insert_game(engine, game_date: date, home_team, away_team):
  Session = sessionmaker(bind=engine)
  session = Session()

  game_id = sha256((str(game_date) + home_team + away_team))

  try:
    new_game = Game(
      id=game_id,
      game_date=date(game_date),
      home_team=home_team,
      away_team=away_team
    )

    session.add(new_game)
    session.commit()
    print(f"New game successfully added: {away_team} @ {home_team} ({game_date})")
  except IntegrityError:
    print(f"Player gamelog already exists: {away_team} @ {home_team} ({game_date})")
    session.close()
  except Exception as e:
    session.rollback()
    print(f"Failed to add game. Error: {traceback.format_exc()}")
  finally:
    session.close()
