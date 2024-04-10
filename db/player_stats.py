from sqlalchemy import select, create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from db.models import PlayerStats
from datetime import date
from hashlib import sha256

# add a player stat row to the DB
def insert_player_stat(engine, game_date, home_team, away_team, is_home_game, player_name, player_age, game_outcome, game_started, minutes_played, points, fg_made, fg_attempted, threes_made, threes_attempted, ft_made, ft_attempted, orb, drb, assists, steals, blocks, turnovers, plus_minus):
  Session = sessionmaker(bind=engine)
  session = Session()
  game_id = sha256((str(game_date.date()) + home_team + away_team).encode('utf-8')).hexdigest()
  stats_id = sha256((str(game_id) + player_name).encode('utf-8')).hexdigest()

  try:
    # create a new PlayerStats instance
    new_player_stats = PlayerStats(
      stats_id=stats_id,
      game_id=game_id,
      game_date=game_date.date(),
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
  except IntegrityError:
    print(f"Player stat already exists")
    session.close()
  except Exception as e:
    session.rollback()
    print(f"Failed to add player stat. Error: {e}")
  finally:
    session.close()

# get all stats for a certain game as a flattened string (for transformer input)
def get_flattened_player_stats_by_game_id(session, game_date, home_team, away_team):
  home_team = home_team.replace("LA Clippers", "Los Angeles Clippers")
  stmt = select(PlayerStats).filter_by(home_team=home_team, away_team=away_team)
  res = session.execute(stmt).all()
  output = f"{game_date} {away_team} at {home_team} "
  non_stats = ['stats_id', 'game_id', 'away_team', 'home_team', 'game_date']

  if len(res) == 0:
    raise ValueError

  for player_stats in res:
    try:
      player_game_date = date(player_stats[0].game_date.date())
    except Exception as e:
      player_game_date = player_stats[0].game_date

    if game_date != player_game_date:
      continue

    inst = inspect(player_stats[0])
    for attr in inst.mapper.column_attrs:
      field_name = attr.key
      if field_name not in non_stats:
        field_value = getattr(player_stats[0], field_name)
        output += f"{field_name}: {field_value} "
  
  return output

# get all stats for a certain player
def get_player_stats_by_player_name(engine, player_name):
  # TODO
  pass
