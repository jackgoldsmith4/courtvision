from utils import remove_special_characters
from db.players import get_player_by_id
from db.models import PlayerGameLog
from db.games import get_game_by_id
from utils import heroku_print
from hashlib import sha256

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

def get_game_log_dicts_by_game_id(session, game_id):
  logs = session.query(PlayerGameLog).filter(PlayerGameLog.game_id == game_id).all()
  return [log.to_dict() for log in logs]

# get all stats for a certain game as a flattened string (for language model input)
def get_flattened_player_game_logs_by_game_id(session, game_id, game_date, home_team, away_team):
  output = f"{game_date} {away_team} @ {home_team}"
  non_stats = ['player_game_log_id', 'player_id', 'game_id']
  players = {}

  game_logs = get_game_log_dicts_by_game_id(session, game_id)
  for log in game_logs:
    player_name = get_player_by_id(session, log['player_id']).name
    player_str = f"player_name: {remove_special_characters(player_name)}"
    points = 0
    for key in log:
      if key not in non_stats:
        if key == 'points':
          points = log[key]

        player_str += f"{key}: {log[key]} "
    players[player_str] = points

  # sort players in the resulting game string from most points to least
  sorted_players = sorted(players, key=lambda k: players[k], reverse=True)
  for player in sorted_players:
    output += player

  return output
