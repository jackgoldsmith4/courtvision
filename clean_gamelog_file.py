# player_df['MP'] = convert_time_to_float(player_df['MP'])

# def convert_time_to_float(time_series):
#   split_series = time_series.str.split(':', expand=True)
#   minutes = split_series[0].astype(int)
#   seconds = split_series[1].astype(int)
#   return round(minutes + seconds / 60, 2)
