import pandas as pd

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
def cows_above_yline(df):
    tags = list()
    keep = list()
    y_line = 2595
    u_cows = unique_cows(df)
    for i in range(len(u_cows)):
        temp = df.loc[df['tag_id'] == u_cows[i]]
        x,y,z = positions(temp)
        if y[0] < y_line:
            tags.append(u_cows[i])
        else:
            keep.append(u_cows[i])
    print(tags)
    df = drop_tags_list(df, tags)
    return df

# function to drop rows with certain tag_ids from list
def drop_tags_list(df, tags):
    for i in range(len(tags)):
        df = df.drop(df[df.tag_id == tags[i]].index)
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

# function to divide cows into groups based on bed preference
def divide_cows(df, barn_filename):

    u_cows = unique_cows(df)   #Get a list of the unique cows ID:s

    barn = pd.read_csv(barn_filename, skiprows=0, sep=';', header=0)            #Read the barn beds coordinates
    barn.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3', 'y4']

    bed1 = barn.iloc[7]         #divide the different beds
    bed2 = barn.iloc[8]
    bed3 = barn.iloc[9]
    bed4 = barn.iloc[10]
    bed5 = barn.iloc[11]
    bed6 = barn.iloc[12]
    bed8 = barn.iloc[13]
    bed9 = barn.iloc[14]

    beds = {0: [],   #Initiate lists of cows
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
            8: []}

    for i in range(len(u_cows)):        #For each cow that has activity type "In cubicle"
        temp = df.loc[df['tag_id'] == u_cows[i]]
        temp = temp.loc[temp['activity_type'] == 3]
        x, y, z = positions(temp)   #Get the positions from the cow
        bed_count = [0]*8

        for j in range(len(x)): #For each position, assign it to a bed
            if is_inside((x[j], y[j]), bed1):
                bed_count[0] += 1
            elif is_inside((x[j], y[j]), bed2):
                bed_count[1] += 1
            elif is_inside((x[j], y[j]), bed3):
                bed_count[2] += 1
            elif is_inside((x[j], y[j]), bed4):
                bed_count[3] += 1
            elif is_inside((x[j], y[j]), bed5):
                bed_count[4] += 1
            elif is_inside((x[j], y[j]), bed6):
                bed_count[5] += 1
            elif is_inside((x[j], y[j]), bed8):
                bed_count[6] += 1
            elif is_inside((x[j], y[j]), bed9):
                bed_count[7] += 1

        if sum(bed_count) != 0:         #If the cow has been in any bed, append its ID to the list of the bed where it spent the most time
            beds[bed_count.index(max(bed_count))].append(u_cows[i])
        else:
            beds[8].append(u_cows[i])   #If none of the cows 'in cubicle' positions could be assigned to a bed, or if there where none, assign to separate list

    return list(beds.values())      #Return a list of lists of the ID:s of cows in different beds

# cow iside bed
def is_inside(pos, bed):
    if bed['x1'] < pos[0] < bed['x3'] and bed['y1'] < pos[1] < bed['y2']:
        return True
    else:
        return False