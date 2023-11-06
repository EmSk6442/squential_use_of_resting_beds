import functions as func
import math

# read file
nrows = 500
df = func.csv_read_FA(FA_20200922T000000UTC, nrows)

# unique cows
u = func.unique_cows(df)
print(len(u))
