import functions as func
import initialization as init
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# read file
barn_file = "barn.csv"
path = '.\\FA-Data\\'
nrows = 0
hours = 3

bed_dir = '.\\beds\\'
try:
    os.mkdir(bed_dir)
except FileExistsError:
    print('File exist')

dir_list = os.listdir(path)
dir_list = [path + file for file in dir_list]
file = dir_list[0]
#for file in dir_list:
df_beds_milk1, df_beds_milk2 = func.mainframe(file, nrows, barn_file, bed_dir, hours)
    
    # undersök kossorna med fler kossor i samma säng
    # plot av ladan med kossor
    