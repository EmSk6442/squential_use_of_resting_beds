import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from random import randint
import math
import matplotlib.lines as mlines
import matplotlib.patches as pat
from matplotlib.animation import FuncAnimation
from matplotlib import transforms
import datetime as datetime
import time
from scipy import stats
import os

# function
def mainframe(file, nrows, barn_file, bed_dir, hours):
    # initialize whole dataframe
    df = csv_read_FA(file, nrows)

    # remove constant transmittors
    df = remove_cons_trans(df)

    # split cows into groups
    g2_df, g1_df = cows_above_yline_right_left(df, barn_file)

    # divide df into milking 1 and milking 2 based on enry to the milking parlor
    g1_df_milk1, g1_df = cows_start_time_milking(g1_df, hours)
    g1_df_milk2, g1_df = cows_start_time_milking(g1_df, hours)

    g2_df_milk1, g2_df = cows_start_time_milking(g2_df, hours)
    g2_df_milk2, g2_df = cows_start_time_milking(g2_df, hours)

    # assign cows to a bed in the
    g1_df_milk1 = assign_cows_to_bed(g1_df_milk1, barn_file)
    g1_df_milk2 = assign_cows_to_bed(g1_df_milk2, barn_file)
    
    g2_df_milk1 = assign_cows_to_bed(g2_df_milk1, barn_file)
    g2_df_milk2 = assign_cows_to_bed(g2_df_milk2, barn_file)

    # initalize dataframe beds
    df_beds_milk1 = bed_data_frame(barn_file)
    df_beds_milk2 = bed_data_frame(barn_file)

    # crossreference cows in bed
    df_beds_milk1 = time_in_bed(g1_df_milk1, df_beds_milk1, 900)
    df_beds_milk1 = time_in_bed(g2_df_milk1, df_beds_milk1, 900)
    
    df_beds_milk2 = time_in_bed(g1_df_milk2, df_beds_milk2, 900)
    df_beds_milk2 = time_in_bed(g2_df_milk2, df_beds_milk2, 900)

    # sort beds by bed and starttimes
    df_beds_milk1 = sort_beds(df_beds_milk1)
    df_beds_milk2 = sort_beds(df_beds_milk2)

    #Save each days data
    name1 = file.replace('.\FA-Data\FA_', '') + '_milk1'
    name1 = name1.replace('.csv', '')
    save_csv(df_beds_milk1, name1, bed_dir)

    name2 = file.replace('.\FA-Data\FA_', '') + '_milk2'
    name2 = name2.replace('.csv', '')
    save_csv(df_beds_milk2, name2, bed_dir)
    
    return df_beds_milk1, df_beds_milk2


# read csv-file
def csv_read_FA(filename, nrows):
    if nrows == 0:
        df = pd.read_csv(filename, header=None)
    else:
        df = pd.read_csv(filename, nrows=nrows, header=None)
    df.columns = ['data_entity', 'tag_id', 'tag_string', 'time', 'x', 'y', 'z']
    return df

# list of all files in directory
def files_in_directory(path):
    dir_list = os.listdir(path)
    return dir_list

# dataframe for beds
def bed_data_frame(barn_filename):
    barn = pd.read_csv(barn_filename, skiprows = 0, sep = ';', header=0)
    df = pd.DataFrame(columns=['bed_id', 'tag_id', 'start_time', 'durration', '%_in_bed'])
    return df

def save_csv(df, name, dir):
    df.to_csv(dir + name + '.csv')

# number of cows
def unique_cows(df):
    return df.tag_id.unique()

def remove_cows_missing_data_points(df):
    df_len = df.groupby("tag_id").size()
    maxlen = df_len.max()
    df_keep = df_len[df_len >= 0.7*maxlen].index
    df = df[df["tag_id"].isin(df_keep)]
    return df

# drop cows under y-line and divide into g1 and g2
def cows_above_yline_right_left(df, barn_filename):
    barn = pd.read_csv(barn_filename, skiprows = 0, sep = ';', header=0)
    left_wall = list(barn['x1'])[0]
    right_wall = list(barn['x3'])[0]
    y_line = 2595

    #Mean above y-line
    mean_cow = df.groupby('tag_id')[['x', 'y']].mean()
    df_keep = mean_cow[mean_cow['y'] >= y_line].index
    df = df[df["tag_id"].isin(df_keep)]
    
    #Mean in either g1 or g2 
    keep_right = mean_cow[mean_cow['x'] >= left_wall + (right_wall+left_wall)/2].index
    keep_left = mean_cow[mean_cow['x'] < left_wall + (right_wall+left_wall)/2].index
    df_g1 = df[df["tag_id"].isin(keep_right)]
    df_g2 = df[df["tag_id"].isin(keep_left)]
    return df_g2, df_g1

def cows_between_time(df, t0, t1):
    #Convert time to epoch time
    t0 = int(time.mktime(t0.timetuple()))*1000
    t1 = int(time.mktime(t1.timetuple()))*1000
    #Select i closest to time
    index_t0 = df.iloc[(df['time']-t0).abs().argsort()[:1]].index
    index_t1 = df.iloc[(df['time']-t1).abs().argsort()[:1]].index
    #Select Dataframe between index
    df = df[df.index.isin(range(index_t0[0], index_t1[0]))]
    return df

# cow srart milking
def cows_start_time_milking(df, hours):
    temp = df[df['y'] < 1310]
    temp = temp.drop_duplicates(['tag_id'], keep = 'first')
    t1 = hours*60*60*1000
    t2 = 4*60*60*1000
    ind1 = df.iloc[(df['time']-(temp['time'].min()+t1)).abs().argsort()[:1]].index
    ind2 = df.iloc[(df['time']-(temp['time'].min()+t2)).abs().argsort()[:1]].index
    df_milk = df.loc[temp['time'].idxmin():ind1[0]]
    df = df.truncate(before=ind2[0])
    return df_milk, df

# find coordinates
def positions(df):
    x = list(df['x'])
    y = list(df['y'])
    z = list(df['z'])
    return x,y,z

# function to assign a cow to bed based on how long the cow is in the bed
def assign_cows_to_beds(df, barn_filename):
    u_cows = unique_cows(df)   #Get a list of the unique cows ID:s

    barn = pd.read_csv(barn_filename, skiprows=0, sep=';', header=0)            #Read the barn beds coordinates
    #barn.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3', 'y4']

    bedarea = []
    for i in range(13, len(barn)):
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
                if is_inside((x[j], y[j]), bedarea[k]) == True:
                    if not is_inside((x[j-1], y[j-1]), bedarea[k]):   #start time when entering booth
                        start_time = time[j]
                    elif is_inside((x[j], y[j]), bedarea[k]) and not is_inside((x[j+1], y[j+1]), bedarea[k]): #stayes in booth
                        stop_time = time[j]
                        if (stop_time - start_time)/1000 > 60:
                            beds[k].append([u_cows[i], start_time, stop_time, round((stop_time - start_time)/1000)])
                            continue
    return beds      #Return a list of lists of the ID:s of cows in different beds

def assign_cows_to_bed(df, barn_filename):
    df["bed_id"] = np.nan
    barn = pd.read_csv(barn_filename, skiprows=0, sep=';', header=0)
    bedarea = list()
    for i in range(13, len(barn)):
        bedarea.append(barn.iloc[i])
    for i in range(len(bedarea)):  
        test = df[(df['x'] >= bedarea[i][1]) & (df['x'] < bedarea[i][3]) & (df['y'] >= bedarea[i][5]) & (df['y'] < bedarea[i][6])].index
        df.loc[test, "bed_id"] = i
    return df
    
# function to sort the cows into a new dataset looking at the beds
def time_in_bed(df, df_beds, points_in_bed):
    df = df.dropna()
    u_cows = unique_cows(df)
    for i in range(len(u_cows)):
        tag_id = u_cows[i]
        temp = df.loc[df['tag_id'] == tag_id]
        bed_numbers = temp.groupby('bed_id').size().max()
        while bed_numbers > points_in_bed:
            bed_number = temp.groupby('bed_id').size().idxmax()
            temp1 = temp.loc[temp['bed_id'] == bed_number]
            #Filter med för långt tid mellan punkterna
            temp1 = outliners(temp1)
            remove = temp.loc[temp1['time'].idxmin():temp1['time'].idxmax()].index
            # write in data into df_beds
            df_beds.loc[len(df_beds)] = {'bed_id': bed_number, 'tag_id': tag_id, 'start_time': temp1['time'].min(), 'durration': round((temp1['time'].max() - temp1['time'].min())/60000), '%_in_bed': round(bed_numbers/len(remove)*100)}
            # remove data when cow is in bed
            temp = temp.drop(remove)
            bed_numbers = temp.groupby('bed_id').size().max()
    return df_beds

def outliners(df):
    # Calculate the z-score for eaxh time
    z = np.abs(stats.zscore(df['time']))
    # Identify outliers with a z-score greater than 3 ie. 99,7 % 
    threshold = 3
    outliers = df[z > threshold]
    # drop rows containing outliers
    df = df.drop(outliers.index)
    return df

# function to sort the cows in bed based on startingtime
def sort_beds_by_start_time(beds):
    for i in range(len(beds)):
        beds[i] = sorted(beds[i], key=lambda value:value[1])
    return beds
    
def sort_beds(df):
    return df.sort_values(by = ['bed_id', 'start_time']).reset_index(drop=True)
    

# cow iside bed
def is_inside(pos, bed):
    if bed['x1'] < pos[0] < bed['x3'] and bed['y1'] < pos[1] < bed['y2']:
        return True
    else:
        return False

def remove_cons_trans(df):
    df = df[~df['tag_id'].astype(str).str.startswith('22')]
    return df

###############################################################################value[]
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

    # function to plot the outline of the barn with colors
def plot_barn_color(filename,df_times):
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

        fig, ax = plt.subplots(1,figsize=(3.75,6))
        for i in range(len(units)):
           art =  pat.Rectangle((x_1[i],min(y_1[i],y_2[i])),x_3[i]-x_1[i], max(y_1[i],y_2[i])-min(y_1[i],y_2[i]), fill = False)
           ax.add_patch(art)

        for i in range(len(df_times)):
            if df_times.values[i] == 1:
                art =  pat.Rectangle((x_1[int(df_times.index[i])+13],min(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13])),x_3[int(df_times.index[i])+13]-x_1[int(df_times.index[i])+13], max(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13])-min(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13]), edgecolor='black', facecolor="lightgreen", linewidth=0.5)
            elif df_times.values[i] == 2:
                art =  pat.Rectangle((x_1[int(df_times.index[i])+13],min(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13])),x_3[int(df_times.index[i])+13]-x_1[int(df_times.index[i])+13], max(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13])-min(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13]), edgecolor='black', facecolor="yellow", linewidth=0.5)
            elif df_times.values[i] == 3:
                art =  pat.Rectangle((x_1[int(df_times.index[i])+13],min(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13])),x_3[int(df_times.index[i])+13]-x_1[int(df_times.index[i])+13], max(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13])-min(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13]), edgecolor='black', facecolor="lightcoral", linewidth=0.5)
            elif df_times.values[i] >= 4:
                art =  pat.Rectangle((x_1[int(df_times.index[i])+13],min(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13])),x_3[int(df_times.index[i])+13]-x_1[int(df_times.index[i])+13], max(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13])-min(y_1[int(df_times.index[i])+13],y_2[int(df_times.index[i])+13]), edgecolor='black', facecolor="black", linewidth=0.5)
            else:
                art =  pat.Rectangle((x_1[i],min(y_1[i],y_2[i])),x_3[i]-x_1[i], max(y_1[i],y_2[i])-min(y_1[i],y_2[i]), fill = False, linewidth=0.5)
            ax.add_patch(art)

        patch1 = mpatches.Patch(color='lightgreen', label='1') 
        patch2 = mpatches.Patch(color='yellow', label='2') 
        patch3 = mpatches.Patch(color='lightcoral', label='3') 
        ax.legend(title='Number of cows',handles=[patch1, patch2, patch3],loc='lower left')
        ax.set_xlim(x_1[0],x_3[0])
        ax.set_ylim(y_1[0],y_2[0])
        return fig, ax


####################################
### Animations                  ####
####################################
pause = False

def animate_cows(df, cowID_1, cowID_2, barn_filename, save_path='n'):

    cow_1 = df.loc[df['tag_id'] == cowID_1]

    cow_2 = df.loc[df['tag_id'] == cowID_2]

    x1, y1, z1 = positions(cow_1)
    x2, y2, z2 = positions(cow_2)

    time1 = list(cow_1['time'])
    time2 = list(cow_2['time'])

    timestrings1= []
    timestrings2 = []

    for timestamp1 in time1:
        timestrings1.append(datetime.date.fromtimestamp((timestamp1/1000)-7200))

    for timestamp2 in time2:
        timestrings2.append(datetime.date.fromtimestamp((timestamp2 / 1000) - 7200))

    f, ax1 = plot_barn(barn_filename)


    ax1.change_geometry(2, 1, 1)
    ax2 = f.add_subplot(212)

    plt.tight_layout()

    pos1 = ax1.get_position().bounds
    pos2 = ax2.get_position().bounds

    new_pos1 = [pos1[0], 0.25, pos1[2], 0.7]
    new_pos2 = [pos2[0], pos2[1], pos2[2], 0.1]

    ax1.set_position(new_pos1)
    ax2.set_position(new_pos2)

    xdata1, ydata1 = [], []
    ln1, = ax1.plot([], [], '-')
    xdata2, ydata2 = [], []
    ln2, = ax1.plot([], [], '-')

    d1, = ax1.plot([], [], 'co', label='Cow '+ str(cowID_1))
    d2, = ax1.plot([], [], 'yo', label='Cow '+ str(cowID_2))

    ax1.legend(loc='upper left')

    dist, time = [], []
    dist_plot, = ax2.plot([], [], 'r-')

    def run_animation():
        ani_running = True
        i = 0
        j = 0
        def onClick(event): #If the window is clicked, the gif pauses
            nonlocal ani_running
            if ani_running:
                ani.event_source.stop()
                ani_running = False
            else:
                ani.event_source.start()
                ani_running = True

        def init():
            ax1.set_xlim(0, 3340)
            ax1.set_ylim(0, 8738)
            ax2.set_xlim(timestrings1[0], timestrings1[len(timestrings1)-1])

            ax2.set_ylim(0, 10000)
            date1 = timestrings1[0]
            date2 = timestrings1[len(timestrings1)-1]
            ax1.set_title("Plot of two cows between " + date1.strftime("%d %b %Y %H:%M") + " - " +
                          date2.strftime("%d %b %Y %H:%M"), fontsize=8)
            ax2.set_ylabel('Distance(cm)')
            ax2.set_xlabel('Time of day')

            return ln1, ln2, d1, d2, dist_plot

        def update(frame):
            nonlocal i
            nonlocal j
            if not pause:
                if time1[i] <= time2[j]:
                    if i == len(time1) - 1:  # if at end of times_1
                        j = j + 1
                        xdata2.append(x2[j])  # new distance
                        ydata2.append(y2[j])
                        xdata1.append(x1[i])  # new distance
                        ydata1.append(y1[i])
                    else:
                        i = i + 1
                        xdata1.append(x1[i])  # new distance
                        ydata1.append(y1[i])
                        xdata2.append(x2[j])  # new distance
                        ydata2.append(y2[j])
                else:
                    if j == len(time2) - 1:  # if at end of times_2
                        i = i + 1
                        xdata1.append(x1[i])  # new distance
                        ydata1.append(y1[i])
                        xdata2.append(x2[j])  # new distance
                        ydata2.append(y2[j])
                    else:
                        j = j + 1
                        xdata2.append(x2[j])  # new distance
                        ydata2.append(y2[j])
                        xdata1.append(x1[i])  # new distance
                        ydata1.append(y1[i])

                ln1.set_data(xdata1, ydata1) #Uppdate the plot with the data
                d1.set_data(x1[i], y1[i])
                ln2.set_data(xdata2, ydata2)
                d2.set_data(x2[j], y2[j])
                dist.append(math.sqrt(math.pow(x1[i]-x2[j], 2) + math.pow(y1[i]-y2[j], 2)))

                if time1[i]<time2[j]: #Uppdate the correct time
                    time.append((timestrings1[i]))
                else:
                    time.append((timestrings2[j]))


                dist_plot.set_data(time, dist)

            return ln1, ln2, d1, d2, dist_plot

        f.canvas.mpl_connect('button_press_event', onClick)
        ani = FuncAnimation(f, update, frames=len(time1)+len(time2)-2, init_func=init, blit=True, interval=1, repeat=False) #Main animationfunction
        if save_path != 'n': #If a filename is given, the gif is saved
            try:
                ani.save(save_path)
            except:
                print('Wrong filepath')

        plt.show()

    run_animation()
