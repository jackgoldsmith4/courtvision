# # rename some cols for clarity
# player_df.rename(columns={
#   'Unnamed: 5': 'Home/Away',
#   'Unnamed: 7': 'Win/Loss',
#   'Rk': 'Game of season',
#   'G': 'Game for player',
#   'Tm': 'Team',
#   'Age': 'Age (days)'
# }, inplace=True)

# # cleanup some of the columns
# player_df['Home/Away'].fillna('H', inplace=True)
# player_df['Home/Away'].replace('@','A', inplace=True)
# player_df['Date'] = pd.to_datetime(player_df['Date'])

# # convert age to days
# years, days = player_df['Age (days)'].str.split('-', expand=True).astype(int).values.T
# player_df['Age (days)'] = player_df['Age (days)'] = years * 365 + days

# player_df['MP'] = convert_time_to_float(player_df['MP'])

# def convert_time_to_float(time_series):
#   split_series = time_series.str.split(':', expand=True)
#   minutes = split_series[0].astype(int)
#   seconds = split_series[1].astype(int)
#   return round(minutes + seconds / 60, 2)
