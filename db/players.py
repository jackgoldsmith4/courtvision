from sqlalchemy.exc import IntegrityError
from utils import heroku_print
from db.db import get_session
from db.models import Player
import traceback

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
    heroku_print(f"New player successfully added: {player_name} (ID: {player_id})")
    return new_player
  except IntegrityError:
    heroku_print(f"Player already exists: {player_name} (ID: {player_id})")
  except:
    session.rollback()
    heroku_print(f"Failed to add player {player_name} (ID: {player_id}). Error: {traceback.format_exc()}")

def get_players(session, after_year = None):
  try:
    players = session.query(Player)
    if after_year:
      players = players.filter(Player.end_year >= after_year)

    players = players.all()
    return [player.to_dict() for player in players]
  except:
    heroku_print(f"Failed retrieve players. Error: {traceback.format_exc()}")

def get_player_by_id(session, player_id):
  return session.query(Player).filter_by(id=player_id).first()

def clean_player_names():
  with get_session() as session:
    players = session.query(Player).all()
    for player in players:
      if '*' in player.name:
        player.name = player.name.replace('*', '')
        heroku_print(f"{player.name} name cleaned.")
        session.commit()
