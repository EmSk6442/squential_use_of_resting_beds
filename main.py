import functions as func
import os
import multiprocessing as mp


# read file
barn_file = "barn.csv"
path = '.\\FA-Data\\'
nrows = 0
hours = 3
hours_to_next_milking = 5
points = 900
# cores = 3

bed_dir = '.\\beds\\'
try:
    os.mkdir(bed_dir)
except FileExistsError:
    print('File exist')

dir_list = os.listdir(path)
dir_list = [path + file for file in dir_list]

for file in dir_list:
    df_beds_milk1, df_beds_milk2 = func.mainframe(file, nrows, barn_file, bed_dir, hours, hours_to_next_milking, points)
