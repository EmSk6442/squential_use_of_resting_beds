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

bed_dir = '.\\beds\\'
try:
    os.mkdir(bed_dir)
except FileExistsError:
    print('File exist')
    
dir_list = func.files_in_directory(path)
dir_list = [path + file for file in dir_list]

for file in dir_list:
    print(file)
    func.mainframe(file, nrows, barn_file, bed_dir, 3)