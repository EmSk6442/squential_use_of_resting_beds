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

df = func.csv_read_FA(file, nrows)

# removes cows with more than 70% datapoints missing 
#df = func.remove_cows_missing_data_points(df)
# sort out cows above y-line and per G1 or G2

g2_df, g1_df = func.cows_above_yline_right_left(df, barn_file)

#print(len(g1_df))
# divide df into milking 1 and milking 2 based on enry to the milking parlor
hours = 4
g1_df_milk1, g1_df = func.cows_start_time_milking(g1_df, hours)
g1_df_milk2, g1_df = func.cows_start_time_milking(g1_df, hours)

g2_df_milk1, g2_df = func.cows_start_time_milking(g2_df, hours)
g2_df_milk2, g2_df = func.cows_start_time_milking(g2_df, hours)

#g2_t0 = datetime.datetime(2020, 9, 22, 7, 0)
#g2_t1 = datetime.datetime(2020, 9, 22, 7 + time_after_milking, 0)
#g2_t2 = datetime.datetime(2020, 9, 22, 18, 30)
#g2_t3 = datetime.datetime(2020, 9, 22, 18 + time_after_milking, 0)
#g2_df_milk1 = func.cows_between_time(g2_df, g2_t0, g2_t1)
#g2_df_milk2 = func.cows_between_time(g2_df, g2_t2, g2_t3)

# assign cows to a bed in the

g1_df_milk2 = func.assign_cows_to_bed(g1_df_milk2, barn_file)

# sort the cows in bed in order of starting time
#Initalize dataframe beds
df_beds = func.bed_data_frame(barn_file)

#Crossreference cows in bed
df_beds = func.time_in_bed(g1_df_milk2, df_beds, 900)

#Sort beds by bed and starttimes
df_beds = func.sort_beds(df_beds)

func.save_csv(df_beds)

# animation
#cowID_1 = 2432025
#cowID_2 = 2432118
#func.animate_cows(df, cowID_1, cowID_2, barn_file, save_path='n')

# visualize
# visualize
#fig,ax = func.plot_barn_color(barn_file,df_number_of_times)
#plt.show()
