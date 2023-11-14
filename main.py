import functions as func
import initialization as init
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import time

# read file
nrows = 15000000
file = "FA_20200922T000000UTC.csv"
barn_file = "barn.csv"

t = time.time()
df = func.csv_read_FA(file, nrows)
elapsed = time.time() - t
print(f'read scv file: ', elapsed)
# removes cows with more than 70% datapoints missing 
#df = func.remove_cows_missing_data_points(df)
# sort out cows above y-line and per G1 or G2
t = time.time()
g2_df, g1_df = func.cows_above_yline_right_left(df, barn_file)
elapsed = time.time() - t
print(f'divide cows: ', elapsed)
#print(len(g1_df))
# divide df into milking 1 and milking 2
g1_t0 = datetime.datetime(2020, 9, 22, 5, 0)
g1_t1 = datetime.datetime(2020, 9, 22, 9, 0)
#g1_t2 = datetime.datetime(2020, 9, 22, 16, 30)
#g1_t3 = datetime.datetime(2020, 9, 22, 20, 30)
g1_df_milk1 = func.cows_between_time(g1_df, g1_t0, g1_t1)
#g1_df_milk2 = func.cows_between_time(g1_df, g1_t2, g1_t2)
#print(len(g1_df_milk1))

#g2_t0 = datetime.datetime(2020, 9, 22, 7, 0)
#g2_t1 = datetime.datetime(2020, 9, 22, 11, 2)
#g2_t2 = datetime.datetime(2020, 9, 22, 18, 30)
#g2_t3 = datetime.datetime(2020, 9, 22, 24, 0)
#g2_df_milk1 = func.cows_between_time(g2_df, g2_t0, g2_t1)
#g2_df_milk2 = func.cows_between_time(g2_df, g2_t2, g2_t3)

# assign cows to a bed in the
t = time.time()
beds = func.assign_cows_to_bed(g1_df_milk1, barn_file)
elapsed = time.time() - t
print(f'assign cows to bed: ', elapsed)
# sort the cows in bed in order of starting time
#beds = func.sort_beds_by_start_time(beds)

#animate_cows(df, cowID_1, cowID_2, barn_filename, save_path='n')

# visualize