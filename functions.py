# read csv-file
def csv_read_FA(filename, nrows):
    if nrows == 0:
        df = pd.read_csv(filename, header=None)
    else:
        df = pd.read_csv(filename, nrows=nrows, header=None)
    df.columns = ['data_entity', 'tag_id', 'tag_string', 'time', 'x', 'y', 'z']
return df

# number of cows
def unique_cows(df):
    return df.tag_id.unique()

# drop cows under y-line and divide into left and right
def cows_above_yline(df, barn_filename):
    barn = pd.read_csv(barn_filename, skiprows = 0, sep = ';', header=0)
    barn.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3','y4']
    y_line = 2595;
    u_cows = unique_cows(df)
    above = []
    for i in range(len(u_cows)):
        temp = df.loc[df['tag_id'] == u_cows[i]]
        x,y,z = positions(temp)
        if y < y_line:
            drop_tags(df, temp)
    return df

# function to drop rows with certain tag_ids
def drop_tags(df, tags_filename):
    tags = pd.read_csv(tags_filename, skiprows = 0, sep = ';', header=0)
    tags.columns = ['position', 'Zx', 'Zy', 'tag_string', 'tag_id']
    tag_ids = list(tags['tag_id'])
    for i in range(len(tag_ids)):
        df = df.drop(df[df.tag_id == tag_ids[i]].index)
    return df

# find coordinates
def positions(df):
    x = list(df['x'])
    y = list(df['y'])
    z = list(df['z'])
    return x,y,z
