from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from db.models import Player
import traceback

def insert_player(engine, player_id, player_name, start_year, end_year):
  Session = sessionmaker(bind=engine)
  session = Session()

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
    session.close()
  except Exception as e:
    session.rollback()
    print(f"Failed to add player. Error: {traceback.format_exc()}")
  finally:
    session.close()
