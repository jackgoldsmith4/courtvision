from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, inspect
from db.models import PlayerGameLog
from utils import heroku_print
from hashlib import sha256
from datetime import date

# add a player stat row to the DB
def insert_player_game_log(session, game, player, is_home_game, player_age, game_outcome, game_started, minutes_played, points, fg_made, fg_attempted, threes_made, threes_attempted, ft_made, ft_attempted, orb, drb, assists, steals, blocks, turnovers, plus_minus):
  id_input = str(game.id) + str(player.name)
  player_game_log_id = sha256(id_input.encode()).digest()

  existing_gamelog = session.query(PlayerGameLog).filter_by(player_game_log_id=player_game_log_id).first()
  if existing_gamelog:
    return

  try:
    new_gamelog = PlayerGameLog(
      player_game_log_id=player_game_log_id,
      game_id=game.id,
      player_id=player.id,
      is_home_game=is_home_game,
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

    session.add(new_gamelog)
    session.commit()
    heroku_print(f"New player gamelog successfully added: {player.name} for game {game.game_date}")
  except Exception as e:
    session.rollback()
    heroku_print(f"Failed to add player gamelog. Error: {e}")

# get all stats for a certain game as a flattened string (for transformer input)
def get_flattened_player_game_logs_by_game_id(session, game_date, home_team, away_team):
  home_team = home_team.replace("LA Clippers", "Los Angeles Clippers")
  stmt = select(PlayerGameLog).filter_by(home_team=home_team, away_team=away_team)
  res = session.execute(stmt).all()

  # TODO change above to just query the PlayerGameLog table based on a game_id

  output = f"{game_date} {away_team} at {home_team} "
  non_stats = ['player_game_log_id', 'game_id', 'away_team', 'home_team', 'game_date']
  players = {}

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
    points = 0
    player_str = ''
    for attr in inst.mapper.column_attrs:
      field_name = attr.key
      if field_name not in non_stats:
        field_value = getattr(player_stats[0], field_name)
        if field_name == 'points':
          points = field_value

        player_str += f"{field_name}: {field_value} "
    players[player_str] = points

  sorted_players = sorted(players, key=lambda k: players[k], reverse=True)
  for player in sorted_players:
    output += player

  return output

# check if stats exist for a player in a year to reduce redundant scraping
def check_if_stats_exist(engine, player_name, year):
  Session = sessionmaker(bind=engine)
  session = Session()
  stmt = select(PlayerGameLog).filter_by(player_name=player_name)
  res = session.execute(stmt).all()
  if len(res) == 0:
    return None
  
  for player_stats in res:
    player_game_date = player_stats[0].game_date
    if player_game_date.strftime('%Y') == str(year):
      session.close()
      return player_game_date

  session.close()
