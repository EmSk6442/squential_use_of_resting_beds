import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from random import randint
import math
import matplotlib.lines as mlines
import matplotlib.patches as pat
from matplotlib.animation import FuncAnimation
from matplotlib import transforms
from datetime import datetime

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

def remove_cows_missing_data_points(df):
    tags = list()
    u_cows = unique_cows(df)
    maxlen = 0
    for i in range(len(u_cows)):
        temp = df.loc[df['tag_id'] == u_cows[i]]
        x,y,z = positions(temp)
        if len(x) > maxlen:
            maxlen = len(x)
    for i in range(len(u_cows)):
        temp = df.loc[df['tag_id'] == u_cows[i]]
        x,y,z = positions(temp)
        if len(x) < maxlen*0.7:
            tags.append(u_cows[i])
    df = drop_tags_list(df, tags)
    return df

# drop cows under y-line and divide into left and right
def cows_above_yline(df, barn_filename):
    barn = pd.read_csv(barn_filename, skiprows = 0, sep = ';', header=0)
    tags = []
    right = []
    left = []
    left_wall = list(barn['x1'])[0]
    right_wall = list(barn['x3'])[0]
    y_line = 2595
    u_cows = unique_cows(df)
    for i in range(len(u_cows)):
        temp = df.loc[df['tag_id'] == u_cows[i]]
        x,y,z = positions(temp)
        if y[0] < y_line:
            tags.append(u_cows[i])
        elif sum(x)/len(x) <= left_wall + (right_wall+left_wall)/2:
            left.append(u_cows[i])
        else:
            right.append(u_cows[i])
    left_df = df[df['tag_id'].isin(left)]
    right_df = df[df['tag_id'].isin(right)]
    return left_df, right_df

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

# function to assign a cow to bed based on how long the cow is in the bed
def assign_cows_to_beds(df, side, barn_filename):
    u_cows = unique_cows(df)   #Get a list of the unique cows ID:s

    barn = pd.read_csv(barn_filename, skiprows=0, sep=';', header=0)            #Read the barn beds coordinates
    barn.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3', 'y4']

    bedarea = []
    for i in range(5, len(barn)):
        bedarea.append(barn.iloc[i])

    beds = {}
    for i in range(len(bedarea)):
        beds[i] = []

    for i in range(len(u_cows)):
        temp = df.loc[df['tag_id'] == u_cows[i]]
        x, y, z = positions(temp)   #Get the positions from the cow
        time = list(temp['time'])
        start_time = time[0]
        stop_time = time[-1]
        for j in range(1, len(x)-1): #For each position, assign it to a bed
            for k in range(len(bedarea)):
                if is_inside((x[j], y[j]), bedarea[k]) and not is_inside((x[j-1], y[j-1]), bedarea[k]):   #start time when entering booth
                    start_time = time[j]
                elif is_inside((x[j], y[j]), bedarea[k]) and not is_inside((x[j+1], y[j+1]), bedarea[k]): #stayes in booth
                    stop_time = time[j]
                    if (stop_time - start_time)/1000 > 180:
                        beds[k].append([u_cows[i], start_time, stop_time, (stop_time - start_time)/1000])
    return beds      #Return a list of lists of the ID:s of cows in different beds


# function to sort the cows in bed based on startingtime
def sort_beds_by_start_time(beds):
    print(beds[0])
    

# cow iside bed
def is_inside(pos, bed):
    if bed['x1'] < pos[0] < bed['x3'] and bed['y1'] < pos[1] < bed['y2']:
        return True
    else:
        return False



###############################################################################
####                               PLOTS                                  #####
###############################################################################

# function to plot the outline of the barn
def plot_barn(filename):
        df = pd.read_csv(filename, skiprows = 0, sep = ';', header=0)
        df.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3','y4']
        units = list(df['Unit'])
        x_1 = list(df['x1'])
        x_2 = list(df['x2'])
        x_3 = list(df['x3'])
        x_4 = list(df['x4'])
        y_1 = list(df['y1'])
        y_2 = list(df['y2'])
        y_3 = list(df['y3'])
        y_4 = list(df['y4'])

        fig, ax = plt.subplots(1,figsize=(6,6))
        for i in range(len(units)):
           art =  pat.Rectangle((x_1[i],min(y_1[i],y_2[i])),x_3[i]-x_1[i], max(y_1[i],y_2[i])-min(y_1[i],y_2[i]), fill = False)
           ax.add_patch(art)
           #print(ax.patches)
        ax.set_xlim(x_1[0]-2000,x_3[0]+2000)
        ax.set_ylim(y_1[0]-2000,y_2[0]+2000)
        return fig, ax

# function to plot the position of a cow (based on tag_id) for FA-data
def plot_cow(df, tag_id, filename_barn):
    fig, ax = plot_barn(filename_barn)
    if hasattr(tag_id, "__len__"):
        for i in tag_id:
            temp = df.loc[df['tag_id'] == i]
            x,y,z = positions(temp)
            plt.plot(x,y,'o--', markersize = 2)
    else:
        temp = df.loc[df['tag_id'] == tag_id]
        x,y,z = positions(temp)
        plt.plot(x,y,'o--', markersize = 2)
    plt.show()
   
# function to plot all cows in a time interval
def plot_time(df, t1, t2):
    temp = df.loc[df['time'] <= t2]
    temp = temp.loc[df['time'] >= t1]
    x,y,z = positions(temp)
    plt.scatter(x,y, s = 2)
    plt.show()
