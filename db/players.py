from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.models import Player
import traceback
import os

def insert_player(session, player_id, player_name, start_year, end_year):
  try:
    new_player = Player(
      id=player_id,
      name=player_name,
      start_year=start_year,
      end_year=end_year,
    )

    session.add(new_player)
    session.commit()
    print(f"New player successfully added: {player_name} (ID: {player_id})")
  except IntegrityError:
    print(f"Player already exists: {player_name} (ID: {player_id})")
  except:
    session.rollback()
    print(f"Failed to add player {player_name} (ID: {player_id}). Error: {traceback.format_exc()}")

def get_players(after_year = None):
  engine = create_engine(os.environ.get("DATABASE_URL"))
  Session = sessionmaker(bind=engine)
  session = Session()

  try:
    players = session.query(Player).filter(Player.final_year >= after_year).all()
    return [player.to_dict() for player in players]
  except:
    print(f"Failed retrieve players. Error: {traceback.format_exc()}")
  finally:
    session.close()
    engine.dispose()
