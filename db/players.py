from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from db.models import Player
import traceback
import os

def insert_player(session, player_id, player_name, start_year, end_year):
  existing_player = session.query(Player).filter_by(id=player_id).first()
  if existing_player:
    return existing_player

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
    return new_player
  except IntegrityError:
    print(f"Player already exists: {player_name} (ID: {player_id})")
  except:
    session.rollback()
    print(f"Failed to add player {player_name} (ID: {player_id}). Error: {traceback.format_exc()}")

def get_players(after_year = None):
  load_dotenv()
  engine = create_engine(os.environ.get("DATABASE_URL"))
  Session = sessionmaker(bind=engine)
  session = Session()

  try:
    players = session.query(Player)
    if after_year:
      players = players.filter(Player.end_year >= after_year)

    players = players.all()
    return [player.to_dict() for player in players]
  except:
    print(f"Failed retrieve players. Error: {traceback.format_exc()}")
  finally:
    session.close()
    engine.dispose()

def get_player_by_id(session, player_id):
  return session.query(Player).filter_by(id=player_id).first()

def clean_player_names():
  load_dotenv()
  engine = create_engine(os.environ.get("DATABASE_URL"))
  Session = sessionmaker(bind=engine)
  session = Session()

  players = session.query(Player).all()
  for player in players:
    if '*' in player.name:
      player.name = player.name.replace('*', '')
      print(f"{player.name} name cleaned.")
      session.commit()
