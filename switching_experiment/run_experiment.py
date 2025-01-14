from utils import remove_special_characters
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.games import get_all_games
from db.players import get_players
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
    to show up in the headline of the Associated Press game recap article.

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

  """ # TODO fill in so the model returns full names of any players in the recap headline as they show up in the box score

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
  return player_names # TODO ensure somehow that this is a list of string player names

# Returns: 2x2x2 array representing changes in model behavior after anonymizing player
# A = model predicts player for the headline BEFORE switching
# B = model predicts player for the headline AFTER switching
# C = player actually shows up in the recap headline
#   outcomes = [
#   [  # C = True
#     [val_000, val_001],  # A = False, B = False / A = False, B = True
#     [val_010, val_011],  # A = True,  B = False / ...
#   ],
#   [  # C = False
#     [val_100, val_101],
#     [val_110, val_111],
#   ],
# ]
def build_player_matrix(games_with_player, name):
  player_matrix = np.zeros((2, 2, 2))
  for box_score_str, recap_headline, predicted_name, predicted_name_anonymous, actual_names in games_with_player:
    # increment corresponding matrix cell
    if name in actual_names:
      if predicted_name == name:
        if predicted_name_anonymous == name:
          player_matrix[0][0][0] += 1
        else:
          player_matrix[0][0][1] += 1
      else:
        if predicted_name_anonymous == name:
          player_matrix[0][1][0] += 1
        else:
          player_matrix[0][1][1] += 1
    else:
      if predicted_name == name:
        if predicted_name_anonymous == name:
          player_matrix[1][0][0] += 1
        else:
          player_matrix[1][0][1] += 1
      else:
        if predicted_name_anonymous == name:
          player_matrix[1][1][0] += 1
        else:
          player_matrix[1][1][1] += 1
  return player_matrix

### SCRIPT ###
engine = create_engine(os.environ.get("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

predictions = pd.DataFrame(columns=['box_score_str', 'recap_headline', 'predicted_name', 'predicted_name_anonymous'])
for game in get_all_games():
  box_score_str = '' # TODO pull and flatten all player stats for this game into a box score string (also normalize each name)
  recap_headline = game.recap_headline
  chosen_name, chosen_name_anonymous = predict_name_from_box_score(box_score_str)
  
  actual_names = pull_names_from_recap_headline(box_score_str, recap_headline)

  predictions = predictions.append({
    'box_score_str': box_score_str,
    'recap_headline': recap_headline,
    'predicted_name': remove_special_characters(chosen_name),
    'predicted_name_anonymous': remove_special_characters(chosen_name_anonymous),
    'actual_names': [remove_special_characters(name) for name in actual_names]
  }, ignore_index=True)

player_matrices = {}
for player in get_players(session):
  # return all games in the dataset that contain that player in the box score
  name = remove_special_characters(player.name)
  games_with_player = predictions[predictions['box_score_str'].str.contains(name)]

  player_matrix = build_player_matrix(games_with_player)
  player_matrices[name] = player_matrix

# TODO save player_matrices somehow

session.close()
engine.dispose()
