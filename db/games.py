from db.models import Game
from hashlib import sha256
from datetime import date
import traceback

def insert_game(session, game_date: date, home_team, away_team):
  game_id_input = str(game_date) + home_team + away_team
  game_id = sha256(game_id_input.encode()).digest()

  existing_game = get_game_by_id(session, game_date, home_team, away_team)
  if existing_game:
    return existing_game

  try:
    new_game = Game(
      id=game_id,
      game_date=game_date,
      home_team=home_team,
      away_team=away_team
    )

    session.add(new_game)
    session.commit()
    print(f"New game successfully added: {away_team} @ {home_team} ({game_date})")
    return new_game
  except Exception as e:
    session.rollback()
    print(f"Failed to add game {away_team} @ {home_team} ({game_date}). Error: {traceback.format_exc()}")

def get_game_by_id(session, game_date: date, home_team, away_team):
  return session.query(Game).filter_by(
    game_date=game_date,
    home_team=home_team,
    away_team=away_team
  ).first()
