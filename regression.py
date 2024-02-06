from sklearn.linear_model import LinearRegression, Lasso
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from utils import thread_func
import pandas as pd
import numpy as np
import os

def run_regressions(player_name):
  train = pd.read_csv(f"./player_game_logs/{player_name}/{player_name}_TRAIN.csv")
  test = pd.read_csv(f"./player_game_logs/{player_name}/{player_name}_TEST.csv")

  # # drop columns that are zero to reduce dimensionality
  # train_columns_to_drop = [col for col in train.columns if train[col].sum() == 0]
  # test_columns_to_drop = [col for col in test.columns if test[col].sum() == 0]
  # cols_to_drop = set(train_columns_to_drop + test_columns_to_drop)
  # print(cols_to_drop)
  # train.drop(columns=cols_to_drop, inplace=True)
  # test.drop(columns=cols_to_drop, inplace=True)

  X_train = train.drop(columns=['PTS'])
  X_test = test.drop(columns=['PTS'])
  y_train = train['PTS']
  y_test = test['PTS']
  n_train = y_train.count()
  n_test = y_test.count()
  test_mean = np.mean(y_test)

  # scale features
  scaler = MinMaxScaler()
  X_train_scaled = scaler.fit_transform(X_train)
  X_test_scaled = scaler.transform(X_test)

  # model 1: Linear Regression
  model = LinearRegression()
  model.fit(X_train_scaled, y_train)

  y_train_pred = model.predict(X_train_scaled)
  mse_train = mean_squared_error(y_train, y_train_pred)
  rmse_train = np.sqrt(mse_train)
  r2_train = r2_score(y_train, y_train_pred)

  y_pred_test = model.predict(X_test_scaled)
  mse_test = mean_squared_error(y_test, y_pred_test)
  rmse_test = np.sqrt(mse_test)
  r2_test = r2_score(y_test, y_pred_test)

  weights = {f"{col}_weight": coef for col, coef in zip(X_train.columns, model.coef_)}
  bias = model.intercept_
  
  summary_df_linreg = pd.DataFrame({
    'model_type': 'LinReg',
    'n_train': n_train,
    'n_test': n_test,
    'mse_train': mse_train,
    'rmse_train': rmse_train,
    'r2_train': r2_train,
    'mse_test': mse_test,
    'rmse_test': rmse_test,
    'r2_test': r2_test,
    'y_test_mean': test_mean,
    'bias': bias,
  }, index=[0])
  for key, value in weights.items():
    summary_df_linreg[key] = value

  # model 2: Lasso Regression
  model = Lasso()
  model.fit(X_train_scaled, y_train)

  y_train_pred = model.predict(X_train_scaled)
  mse_train = mean_squared_error(y_train, y_train_pred)
  rmse_train = np.sqrt(mse_train)
  r2_train = r2_score(y_train, y_train_pred)

  y_pred_test = model.predict(X_test_scaled)
  mse_test = mean_squared_error(y_test, y_pred_test)
  rmse_test = np.sqrt(mse_test)
  r2_test = r2_score(y_test, y_pred_test)

  weights = {f"{col}_weight": coef for col, coef in zip(X_train.columns, model.coef_)}
  bias = model.intercept_
  
  summary_df_lasso = pd.DataFrame({
    'model_type': 'Lasso',
    'n_train': n_train,
    'n_test': n_test,
    'mse_train': mse_train,
    'rmse_train': rmse_train,
    'r2_train': r2_train,
    'mse_test': mse_test,
    'rmse_test': rmse_test,
    'r2_test': r2_test,
    'y_test_mean': test_mean,
    'bias': bias,
  }, index=[0])
  for key, value in weights.items():
    summary_df_lasso[key] = value

  # model 3: Random Forest Regression (100 estimators, 20 depth)
  model = RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
  )
  model.fit(X_train, y_train)

  y_train_pred = model.predict(X_train)
  mse_train = mean_squared_error(y_train, y_train_pred)
  rmse_train = np.sqrt(mse_train)
  r2_train = r2_score(y_train, y_train_pred)

  y_pred_test = model.predict(X_test)
  mse_test = mean_squared_error(y_test, y_pred_test)
  rmse_test = np.sqrt(mse_test)
  r2_test = r2_score(y_test, y_pred_test)
  
  summary_df_rf = pd.DataFrame({
    'model_type': 'Random Forest (100 estimators, 20 depth)',
    'n_train': n_train,
    'n_test': n_test,
    'mse_train': mse_train,
    'rmse_train': rmse_train,
    'r2_train': r2_train,
    'mse_test': mse_test,
    'rmse_test': rmse_test,
    'r2_test': r2_test,
    'y_test_mean': test_mean,
  }, index=[0])

  # model 4: Random Forest Regression (50 estimators, 10 depth)
  model = RandomForestRegressor(
    n_estimators=50,
    max_depth=10,
  )
  model.fit(X_train, y_train)

  y_train_pred = model.predict(X_train)
  mse_train = mean_squared_error(y_train, y_train_pred)
  rmse_train = np.sqrt(mse_train)
  r2_train = r2_score(y_train, y_train_pred)

  y_pred_test = model.predict(X_test)
  mse_test = mean_squared_error(y_test, y_pred_test)
  rmse_test = np.sqrt(mse_test)
  r2_test = r2_score(y_test, y_pred_test)
  
  summary_df_rf_2 = pd.DataFrame({
    'model_type': 'Random Forest (50 estimators, 10 depth)',
    'n_train': n_train,
    'n_test': n_test,
    'mse_train': mse_train,
    'rmse_train': rmse_train,
    'r2_train': r2_train,
    'mse_test': mse_test,
    'rmse_test': rmse_test,
    'r2_test': r2_test,
    'y_test_mean': test_mean,
  }, index=[0])

  summary_df = pd.concat([summary_df_linreg, summary_df_lasso, summary_df_rf, summary_df_rf_2])
  summary_df.to_csv(f"./player_game_logs/{player_name}/{player_name}_SUMMARY.csv", index=False)

def regression_wrapper(player_names):
  for name in player_names:
    print(f"Running regressions: {name}")
    run_regressions(name)

######## SCRIPT: run clean function on all NBA players
NUM_THREADS = 5
thread_func(NUM_THREADS, regression_wrapper, os.listdir('./player_game_logs'))
