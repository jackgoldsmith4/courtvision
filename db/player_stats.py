from sqlalchemy.orm import sessionmaker
from db.models import PlayerStats
from hashlib import sha256

# add a player stat row to the DB
def insert_player_stat(engine, game_date, home_team, away_team, is_home_game, player_name, player_age, game_outcome, game_started, minutes_played, points, fg_made, fg_attempted, threes_made, threes_attempted, ft_made, ft_attempted, orb, drb, assists, steals, blocks, turnovers, plus_minus):
  Session = sessionmaker(bind=engine)
  session = Session()
  game_id = sha256((str(game_date) + home_team + away_team).encode('utf-8')).hexdigest()

  


# get all stats for a certain game
def get_player_stats_by_game_id(engine, game_id):
  pass

# get all stats for a certain player
def get_player_stats_by_player_name(engine, player_name):
  # TODO
  pass
