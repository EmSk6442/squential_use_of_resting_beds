import functions as func
import initialization as init
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import time
import os

# read file
file = "FA_20200922T000000UTC.csv"
barn_file = "barn.csv"
path = '.\FA-Data\\'
nrows = 0

new_dir = '.\\beds\\'
try:
    os.mkdir(new_dir)
except FileExistsError:
    print('File exist')
    

dir_list = func.files_in_directory(path)

dir_list = [path + file for file in dir_list]

file = dir_list[0]

df = func.csv_read_FA(file, nrows)

# remove constant transmittors
df = func.remove_cons_trans(df)

# removes cows with more than 70% datapoints missing 
#df = func.remove_cows_missing_data_points(df)
# sort out cows above y-line and per G1 or G2

g2_df, g1_df = func.cows_above_yline_right_left(df, barn_file)

#print(len(g1_df))
# divide df into milking 1 and milking 2 based on enry to the milking parlor
hours = 3
g1_df_milk1, g1_df = func.cows_start_time_milking(g1_df, hours)
g1_df_milk2, g1_df = func.cows_start_time_milking(g1_df, hours)

g2_df_milk1, g2_df = func.cows_start_time_milking(g2_df, hours)
g2_df_milk2, g2_df = func.cows_start_time_milking(g2_df, hours)

# assign cows to a bed in the

g1_df_milk2 = func.assign_cows_to_bed(g1_df_milk2, barn_file)

# sort the cows in bed in order of starting time
#Initalize dataframe beds
df_beds_milk1 = func.bed_data_frame(barn_file)

#Crossreference cows in bed
df_beds_milk1 = func.time_in_bed(g1_df_milk2, df_beds_milk1, 900)

#Sort beds by bed and starttimes
df_beds_milk1 = func.sort_beds(df_beds_milk1)

df_beds_milk2 = func.bed_data_frame(barn_file)

#Crossreference cows in bed
df_beds_milk2 = func.time_in_bed(g1_df_milk2, df_beds_milk2, 900)

#Sort beds by bed and starttimes
df_beds_milk2 = func.sort_beds(df_beds_milk2)

#Save each days data
name1 = file.replace('.\FA-Data\FA_', '') + '_milk1'
name1 = name1.replace('.csv', '')
func.save_csv(df_beds_milk1, name1, new_dir)

name2 = file.replace('.\FA-Data\FA_', '') + '_milk2'
name2 = name2.replace('.csv', '')
func.save_csv(df_beds_milk2, name2, new_dir)

# animation
#cowID_1 = 2432025
#cowID_2 = 2432118
#func.animate_cows(df, cowID_1, cowID_2, barn_file, save_path='n')

# visualize
# visualize
#fig,ax = func.plot_barn_color(barn_file,df_number_of_times)
#plt.show()
