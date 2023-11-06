import functions as func

# read file
nrows = 100000
file = "FA_20200922T000000UTC.csv"
df = func.csv_read_FA(file, nrows)

# unique cows
u = func.unique_cows(df)
print(len(u))
print(len(df))

# sort out cows
df = func.cows_above_yline(df)

# unique cows
u = func.unique_cows(df)
print(len(u))
print(len(df))


## after milking

# for each bed check which cows lay in th bed in order

# identify beds

# init time when milking

# cows in bed, store cow tag id and time t_0 and t_1 in bed

# visualize