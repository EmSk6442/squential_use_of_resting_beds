import polars as pl
import time

def main():
    file = '.\\FA-Data\\FA_20200919T000000UTC.csv'
    barn = '.\\barn.csv'
    t = time.time()
    df = csv_read_FA(file)
    barn = pl.read_csv(barn, separator=';')
    points = 900
    
    df_g1, df_g2 = cows_above_yline_right_left(df, barn)

    # divide df into milking 1 and milking 2 based on enry to the milking parlor
    g1_df_milk1, g1_df = cows_start_time_milking(g1_df, hours)
    g1_df_milk2, g1_df = cows_start_time_milking(g1_df, hours)
    g2_df_milk1, g2_df = cows_start_time_milking(g2_df, hours)
    g2_df_milk2, g2_df = cows_start_time_milking(g2_df, hours)
    
    t = time.time()
    df_g1 = assign_bed_id(df, barn)
    print((time.time() - t))
    print(df_g1)
    
    #df_g1 = df.group_by(['tag_id', 'bed_id']).count()
    
    #df_beds = pl.DataFrame(schema=['bed_id', 'tag_id', 'start_time', 'durration', '%_in_bed'])
    
    #print(df_beds)

    # crossreference cows in bed
    df_beds_milk1 = time_in_bed(g1_df_milk1, df_beds_milk1, 900)
    df_beds_milk1 = time_in_bed(g2_df_milk1, df_beds_milk1, 900)
    
    df_beds_milk2 = time_in_bed(g1_df_milk2, df_beds_milk2, 900)
    df_beds_milk2 = time_in_bed(g2_df_milk2, df_beds_milk2, 900)
    

def csv_read_FA(file):
    df = pl.read_csv(file, new_columns=['data_entity', 'tag_id', 'tag_string', 'time', 'x', 'y', 'z'])
    df = df.drop('z')
    df = df.with_columns(pl.lit(None).alias('bed_id'))
    return df

def cows_above_yline_right_left(df, barn):
    y_line = 1695
    left_wall = barn['x1'][0]
    right_wall = barn['x3'][0]
    
    # cows above y-line
    mean_cow = df.group_by('tag_id', maintain_order=True).mean()
    mean_cow = mean_cow.filter(mean_cow['y'] >= y_line)
    
    # separate cows on g1 and g2 
    keep_right = mean_cow.filter(mean_cow['x'] >= left_wall + (right_wall+left_wall)/2)['tag_id']
    keep_left = mean_cow.filter(mean_cow['x'] < left_wall + (right_wall+left_wall)/2)['tag_id']
    df_g1 = df.filter(df['tag_id'].is_in(keep_right))
    df_g2 = df.filter(df['tag_id'].is_in(keep_left))
    return df_g1, df_g2

# cow srart milking
def cows_start_time_milking(df, hours):
    temp = df.filter(pl.col("y") < 1310)
    temp = temp.unique(subset=["tag_id"], keep="first", maintain_order=True)
    t1 = hours*60*60*1000+temp['time'].min()
    t2 = 4*60*60*1000+temp['time'].min()
    start = (df.select((df['time'] - temp['time'].min()).abs().arg_sort())).limit(1)
    ind1 = (df.select((df['time'] - t1).abs().arg_sort())).limit(1)
    ind2 = (df.select((df['time'] - t2).abs().arg_sort())).limit(1)
    df_milk = df.select(pl.all().slice(start[0]['time'], ind1[0]['time']))
    df = df.select(pl.all().slice(ind2[0]['time'], len(df)))
    return df_milk, df

def assign_cows_to_bed(df, barn):
    bedarea = barn[13:]
    i = 0
    temp = df.with_columns(pl.when((df['x'] >= bedarea['x1'][i]) & (df['x'] < bedarea['x3'][i]) & (df['y'] >= bedarea['y1'][i]) & (df['y'] < bedarea['y2'][i])).then(i).alias('bed_id'))
    for i in range(1, len(bedarea)):
        temp = df.with_columns(pl.when((df['x'] >= bedarea['x1'][i]) & (df['x'] < bedarea['x3'][i]) & (df['y'] >= bedarea['y1'][i]) & (df['y'] < bedarea['y2'][i])).then(i).otherwise(temp['bed_id']).alias('bed_id'))
    return temp

def assign_bed_id(df, bedarea):
    conditions = [
        (df['x'] >= bedarea['x1'][i]) &
        (df['x'] < bedarea['x3'][i]) &
        (df['y'] >= bedarea['y1'][i]) &
        (df['y'] < bedarea['y2'][i])
        for i in range(len(bedarea))
        ]

    df = df.with_columns(pl.when(conditions[0]).then(0).alias('bed_id'))

    for i in range(1, len(bedarea)):
        df = df.with_columns(pl.when(conditions[i]).then(i).otherwise(df['bed_id']).alias('bed_id'))
    return df

# function to sort the cows into a new dataset looking at the beds
def time_in_bed(df, df_beds, points_in_bed):
    #df = df.dropna()
    df = df.drop_nulls()
    beds_tags = df.group_by(['tag_id', 'bed_id']).count()
    max_bed_numbers = beds_tags.filter(pl.col('size') == beds_tags['count'].max())
    while max_bed_numbers[0,2] > points_in_bed:
        temp = df.filter((pl.col("bed_id") == max_bed_numbers[0, 1]) & (pl.col("tag_id") == max_bed_numbers[0, 0]))
        temp = outliers(temp)
        remove = df.select(pl.all().slice(temp['time'].min(), temp['time'].max()))
        df_beds = pl.DataFrame({})
        new_row = pl.DataFrame({"bed_id": [max_bed_numbers[0,1]],"tag_id": [max_bed_numbers[0,0]], "start_time": temp["time"].min(), "durration": round((temp["time"].max() - temp["time"].min())/60000), "%_in_bed": round(max_bed_numbers[0,2]/len(remove)*100)})
        df_beds = pl.concat([df_beds, new_row])
        mask = (df["time"] >= temp['time'].min()) & (df["time"] <= temp['time'].max())
        df = df.filter(~mask)
        max_bed_numbers = df.filter(pl.col('size') == df['count'].max())
    return df_beds

def outliers(df):
    # Calculate the z-score for eaxh time
    z = np.abs(stats.zscore(df['time']))
    # Identify outliers with a z-score greater than 3 ie. 99,7 % 
    threshold = 3
    outliers = df[z > threshold]
    # drop rows containing outliers
    df = df.drop(outliers)
    return df

def sort_beds(df_bed):
    df_bed = df_bed.sort(['bed_id', 'start_time'])
    return df_bed

main()
