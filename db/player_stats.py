from sqlalchemy.orm import sessionmaker
from db.models import PlayerStats
from hashlib import sha256

# add a player stat row to the DB
def insert_player_stat(engine, game_date, home_team, away_team, is_home_game, player_name, player_age, game_outcome, game_started, minutes_played, points, fg_made, fg_attempted, threes_made, threes_attempted, ft_made, ft_attempted, orb, drb, assists, steals, blocks, turnovers, plus_minus):
  Session = sessionmaker(bind=engine)
  session = Session()
  game_id = sha256((str(game_date) + home_team + away_team).encode('utf-8')).hexdigest()
  stats_id = sha256((str(game_id) + player_name).encode('utf-8')).hexdigest()

  try:
    # create a new PlayerStats instance
    new_player_stats = PlayerStats(
      stats_id=stats_id,
      game_id=game_id,
      game_date=game_date,
      home_team=home_team,
      away_team=away_team,
      is_home_game=is_home_game,
      player_name=player_name,
      player_age=player_age,
      game_outcome=game_outcome,
      game_started=game_started,
      minutes_played=minutes_played,
      points=points,
      field_goals_made=fg_made,
      field_goals_attempted=fg_attempted,
      three_pointers_made=threes_made,
      three_pointers_attempted=threes_attempted,
      free_throws_made=ft_made,
      free_throws_attempted=ft_attempted,
      offensive_rebounds=orb,
      defensive_rebounds=drb,
      assists=assists,
      steals=steals,
      blocks=blocks,
      turnovers=turnovers,
      plus_minus=plus_minus
    )

    # add the new instance to the session and commit it to the database
    session.add(new_player_stats)
    session.commit()
    print("New player stat successfully added.")
  except Exception as e:
    session.rollback()
    print(f"Failed to add game recap. Error: {e}")
  finally:
    session.close()

# get all stats for a certain game as a flattened string (for transformer input)
def get_flattened_player_stats_by_game_id(engine, game_id):
  pass

# get all stats for a certain player
def get_player_stats_by_player_name(engine, player_name):
  # TODO
  pass
