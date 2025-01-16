from db.player_game_logs import get_flattened_player_game_logs_by_game_id
from utils import remove_special_characters, heroku_print
from db.games import get_all_games_with_recaps
from db.players import get_players
from db.db import get_session
from openai import OpenAI
import pandas as pd
import numpy as np
import os

url = "https://api.openai.com/v1/chat/completions"
api_key = os.environ.get("OPENAI_API_KEY")
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# prompt GPT 4o mini to pick a player from the given context that will appear in the recap headline
# Returns: name of a player from the context
def prompt_model_to_choose_name(context_str):
  prompt_text = f"""
    Here is a string that represents the box score for a specific NBA game:

    {context_str}

    Your job is to pick the player in this box score that you think is most likely
    to show up in the headline of the game recap article on NBA.com.

    Your response should only consist of a name that is present in the provided box score,
    or just the word None if you think it is most likely that the headline doesn't mention a specific player.

    Some box scores have been anonymized, and each player in that game is represented as Player X, where X is an incrementing integer.
    In these anonymized cases, and only these cases, your response should only consist of the words Player X,
    where X is replaced by the integer corresponding to the player you pick. You can also choose to pick no player and return None.
    In other words, treat anonymized player labels as if they were player names.
    If the names are not anonymized, your response should contain the actual player name instead of an anonymized version.
  """

  client = OpenAI(api_key=api_key)
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {
        "role": "user",
        "content": prompt_text,
      }
    ],
    temperature=0.3,
    max_tokens=60,
    top_p=0.5,
  )

  chosen_player = response.choices[0].message.content
  return chosen_player

# Takes in a box score string and returns an anonymized version, as well as a dictionary
# mapping anonymized names to actual player names {key=anonymized_name, value=player_name}
def anonymize_context(box_score_str):
  player_dict = {}

  player_anonymized_counter = 0
  names = box_score_str.split('player_name: ')[1:]
  for name in names:
    player = name.split(' player_age:')[0]
    anon_player = f"Player {player_anonymized_counter}"
    box_score_str = box_score_str.replace(player, anon_player)
    player_dict[anon_player] = player
    player_anonymized_counter += 1

  return box_score_str, player_dict

# Wrapper function to prompt the model for a box score string and return names chosen before and after anonymization
def predict_name_from_box_score(box_score_str):
  chosen_name = prompt_model_to_choose_name(box_score_str)
  box_score_player_replaced, player_dict = anonymize_context(box_score_str)
  chosen_name_replaced = prompt_model_to_choose_name(box_score_player_replaced)
  try:
    chosen_name_anonymous = player_dict[chosen_name_replaced]
  except KeyError:
    chosen_name_anonymous = 'None'
  return (chosen_name, chosen_name_anonymous)

def pull_names_from_recap_headline(box_score_str, recap_headline) -> list:
  prompt_text = f"""
    Here is a string that represents the box score for a specific NBA game: {box_score_str}
    Here is the Associated Press recap headline for the same game: {recap_headline}

    Your job is to pull out the names of any players that show up in the recap headline, exactly as they appear in the box score.
    For example, if the recap headline is "Smith scores 10 as Nuggets top Blazers 116-108", pull out the full name of the player that "Smith" refers to and return it.
    Recap headlines may contain no players, one player, or multiple players. Find any players referenced in the headline and return their full names exactly as they appear in the box score.
    If there are no players mentioned in the recap headline, return "None".
    If there are multiple players mentioned, return the name of each player separated by commas.

    Return only player name or names. Do not add anything else, and return the name exactly as it shows up in the box score. Do not explain your reasoning.
  """

  client = OpenAI(api_key=api_key)
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {
        "role": "user",
        "content": prompt_text,
      }
    ],
    temperature=0,
    max_tokens=120,
    top_p=0.5,
  )

  player_names = response.choices[0].message.content
  return player_names.split(', ')

# Returns: 2x2x2 array representing changes in model behavior after anonymizing player
# A = player actually shows up in the recap headline (name in actual_names)
# B = model predicts player for the headline BEFORE anonymization (name == predicted_name)
# C = model predicts player for the headline AFTER anonymization (name == predicted_name_anonymous)
#   outcomes = [
#   [  # A = False
#     [val_000, val_001],  # B = False, C = False / B = False, C = True
#     [val_010, val_011],  # B = True,  C = False / B = True, C = True
#   ],
#   [  # A = True
#     [val_100, val_101],
#     [val_110, val_111],
#   ],
# ]
def build_player_matrix(games_with_player, name):
  player_matrix = np.zeros((2, 2, 2))
  for index, game_row in games_with_player.iterrows():
    (box_score_str, recap_headline, predicted_name, predicted_name_anonymous, actual_names) = game_row
    # increment corresponding matrix cell
    if name in actual_names:
      if predicted_name == name:
        if predicted_name_anonymous == name:
          player_matrix[1][1][1] += 1
        else:
          player_matrix[1][1][0] += 1
      else:
        if predicted_name_anonymous == name:
          player_matrix[1][0][1] += 1
        else:
          player_matrix[1][0][0] += 1
    else:
      if predicted_name == name:
        if predicted_name_anonymous == name:
          player_matrix[0][1][1] += 1
        else:
          player_matrix[0][1][0] += 1
      else:
        if predicted_name_anonymous == name:
          player_matrix[0][0][1] += 1
        else:
          player_matrix[0][0][0] += 1
  return player_matrix

### SCRIPT ###=
# predictions = pd.DataFrame(columns=['box_score_str', 'recap_headline', 'predicted_name', 'predicted_name_anonymous'])
predictions = pd.read_csv('predictions.csv')
with get_session() as session:
  games = get_all_games_with_recaps(session)

for index, game in enumerate(games):
  with get_session() as session:
    heroku_print(f"Making recap predictions for game: {game.game_date} {game.away_team} @ {game.home_team} ({index+1}/{len(games)})")

    recap_headline = game.recap_headline
    if recap_headline in predictions['recap_headline'].values:
      heroku_print("Predictions already made for this game.")
      continue
    box_score_str = get_flattened_player_game_logs_by_game_id(session, game.id, game.game_date, game.home_team, game.away_team)

    # LLM calls
    chosen_name, chosen_name_anonymous = predict_name_from_box_score(box_score_str)
    actual_names = pull_names_from_recap_headline(box_score_str, recap_headline)

    new_row = {
      'box_score_str': box_score_str,
      'recap_headline': recap_headline,
      'predicted_name': remove_special_characters(chosen_name),
      'predicted_name_anonymous': remove_special_characters(chosen_name_anonymous),
      'actual_names': [remove_special_characters(name) for name in actual_names]
    }

    predictions = pd.concat([predictions, pd.DataFrame([new_row])], ignore_index=True)

    # periodically save results
    if index % 10 == 0:
      predictions.to_csv('predictions.csv', index=False)
      heroku_print("Predictions saved.")
predictions.to_csv('predictions.csv', index=False)

# From predictions, build a matrix for each player
player_matrices = pd.DataFrame(columns=["player_name", "player_matrix"])
with get_session() as session:
  players = get_players(session)
for index, player in enumerate(players):
  heroku_print(f"Processing player: {player['name']} ({index+1}/{len(players)})")
  
  # return all games in the dataset that contain that player in the box score
  name = remove_special_characters(player['name'])
  name = name[:-1]
  games_with_player = predictions[predictions['box_score_str'].str.contains(name)]

  if len(games_with_player) == 0:
    heroku_print("No games for player.")
    continue

  player_matrix = build_player_matrix(games_with_player, name)
  new_row = {
    'player_name': name,
    'player_matrix': player_matrix
  }
  player_matrices = pd.concat([player_matrices, pd.DataFrame([new_row])], ignore_index=True)
  if index % 10 == 0:
    player_matrices.to_csv('player_matrices.csv', index=False)
player_matrices.to_csv('player_matrices.csv', index=False)
