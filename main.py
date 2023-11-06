import functions as func
import initialization as init
import matplotlib.pyplot as plt

# read file
nrows = 100000
file = "FA_20200922T000000UTC.csv"
df = func.csv_read_FA(file, nrows)

# unique cows
u = func.unique_cows(df)

# sort out cows
df = func.cows_above_yline(df)

# unique cows
u = func.unique_cows(df)

lst = func.assign_cows_to_beds(df, 'barn.csv')

## after milking for each bed check which cows lay in th bed in order

# identify beds

# init time when milking

# cows in bed, store cow tag id and time t_0 and t_1 in bed

# visualize