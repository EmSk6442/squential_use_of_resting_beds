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
    
    t = time.time()
    df_g1 = assign_bed_id(df, barn)
    print((time.time() - t))
    print(df_g1)
    
    #df_g1 = df.group_by(['tag_id', 'bed_id']).count()
    
    #df_beds = pl.DataFrame(schema=['bed_id', 'tag_id', 'start_time', 'durration', '%_in_bed'])
    
    #print(df_beds)
    

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

def time_in_bed(df, df_bed, points):
    
    df = df.group_by(['tag_id', 'x']).count()
    # drop slice
    return

main()