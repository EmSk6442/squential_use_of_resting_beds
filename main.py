import functions as func
import initialization as init
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# read file
nrows = 100000
file = "FA_20200922T000000UTC.csv"
barn_file = "barn.csv"
df = func.csv_read_FA(file, nrows)

df = func.remove_cows_missing_data_points(df)
u_cows = func.unique_cows(df)
print(len(u_cows))

# sort out cows
left_df, right_df = func.cows_above_yline(df, barn_file)
u_cows_left = func.unique_cows(left_df)
u_cows_right = func.unique_cows(right_df)
print(len(u_cows_left), len(u_cows_right))

beds = func.assign_cows_to_beds(df, 'left', barn_file)

beds = func.sort_beds_by_start_time(beds)

## after milking for each bed check which cows lay in th bed in order

# identify beds

# init time when milking

# cows in bed, store cow tag id and time t_0 and t_1 in bed

# visualize