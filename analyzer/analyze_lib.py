#!/usr/bin/env python3

#===================================================================================================================================
# LIBRARIES
#===================================================================================================================================

import os, sys
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#===================================================================================================================================
# GLOBAL FUNCTIONS
#===================================================================================================================================

# convert seconds to hours:minutes:seconds
def s_to_hms(s):
    h, tmp = divmod(s, 3600)
    m, s = divmod(tmp, 60)
    return "%i:%02i:%02i" %(h,m,s)

# compute pace (in km/h and min/km) from distance (m) and time (s)
def compute_pace(d, t):
    if t<1.0:
        return 0.0, 0.0
    else:
        out1 = d/t*3.6
        tmp = t/d*10**3
        m, s = divmod(tmp, 60)
        out2 = "%2i:%02i min/km" %(m,s)  
        return out1, out2

#===================================================================================================================================
# CLASS DATASET
#===================================================================================================================================

class dataset:

    #===============================================================================================================================
    # INIT
    #===============================================================================================================================

    def __init__(self, file_path):

        # read file
        if os.path.exists(file_path):

            self.path = file_path
            self.preprocess()

        else:

            raise FileNotFoundError( "No such file or directory: " + repr(file_path) )

    #===============================================================================================================================
    # PREPROCESS: READ AND PROCESS DATASET
    #===============================================================================================================================

    def preprocess(self):

        # read original file
        df = pd.read_csv(self.path)

        # columns to keep
        c_to_keep = [
            'Activity Date',
            'Activity Type',
            'Elapsed Time.1',
            'Moving Time',
            'Distance.1',
            'Elevation Gain',
            'Average Heart Rate',
        ]

        # check language: EN
        if df.columns[0]=='Activity ID':

            # set date format
            date_format = '%b %d, %Y, %I:%M:%S %p'

        # else: FR
        else:

            # set date format
            locale.setlocale(locale.LC_TIME, 'fr_FR')
            date_format = '%d %b %Y à %H:%M:%S'

            # rename columns
            c_names = [
                "Date de l'activité",
                "Type d'activité",
                "Temps écoulé.1",
                "Durée de déplacement",
                "Distance.1",
                "Dénivelé positif",
                "Fréquence cardiaque moyenne",
            ]
            c_names_dict = dict(zip(c_names, c_to_keep))
            df = df.rename(columns=c_names_dict)

            # rename activity types
            list1 = ["Course à pied", "Vélo", "Randonnée", "Marche"]
            list2 = ['Run', 'Ride', 'Hike', 'Walk']
            df['Activity Type'] = df['Activity Type'].replace(list1, list2)

        # extract desired columns
        df = df[c_to_keep]

        # rename columns (avoid spaces)
        df.columns = [c.replace(' ', '_') for c in df.columns]

        # convert date to datetime format
        formatted_col = pd.to_datetime(df['Activity_Date'], format=date_format)
        df = df.assign(Activity_Date=formatted_col)

        # sort by date
        df = df.sort_values(by='Activity_Date')

        # correct elevation gain: if NaN then 0.0
        df['Elevation_Gain'] = df['Elevation_Gain'].fillna(0.0)
        
        # compute week numbers
        df['Week_Number'] = df['Activity_Date'].dt.isocalendar().week

        # save processed dataframe to class object
        self.df = df

    #===============================================================================================================================
    # ANNUAL ANALYSIS
    #===============================================================================================================================

    def annual_analysis(self, year, sport='All', output_dir='./res', threshold=0.0):

        ## I) Extract specific dataframe

        # keep data from selected year in local dataframe
        df = self.df.loc[self.df['Activity_Date'].dt.year==year]

        # extract specific activities (sport type)
        if sport!='All': df = df.loc[df['Activity_Type'].astype(str)==sport]

        # get number of activites
        n0 = df.shape[0]

        ## II) Summary of fundamentals data (time, distance and elevation)

        # sum along columns
        c = ['Elapsed_Time.1', 'Moving_Time', 'Distance.1', 'Elevation_Gain']
        c_sum = df[c].sum(axis=0)

        # compute pace
        p1, p2 = compute_pace(c_sum['Distance.1'], c_sum['Moving_Time'])

        ## III) Apply filter, summary of heart rate data

        # filter activities if distance threshold is given
        if threshold>0.0: df = df[df['Distance.1']>threshold]

        # update number of activities
        n_act = df.shape[0]

        # count number of filtered activities
        n_filtered = n0 - n_act

        # get number of activites with available HR data
        n_act_HR = df['Average_Heart_Rate'].count()

        # set flag if all activities of the year have missing HR data
        all_HR_missing = True if n_act_HR==0 else False

        # compute number of activites without HR data
        n_act_no_HR = n_act - n_act_HR

        # compute average bpm
        if not all_HR_missing: avg_bpm = df['Average_Heart_Rate'].sum() / n_act_HR

        ## IV) Output (.txt file or in console)

        # create output folder if not existing
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        # set up output file path
        output_file = output_dir + '/' + str(year) + '_' + sport + '.txt'

        with open(output_file, 'w') as f:

            print("\n========== %i ==========" %year, file=f)

            # if no activities were found for the requested year
            if n_act==0:

                print("\nNo activity found.", file=f)

            # else write in file
            else:

                print(f"\nActivities recorded: {n_act:>5}", file=f)
                print(f"Activities w/o HR: {n_act_no_HR:>7}", file=f)
                print(f"Threshold: {threshold:>13.2f} m", file=f)
                print(f"Activities filtered: {n_filtered:>5}", file=f)
                print(f"\n- Elapsed Time: {s_to_hms(c_sum['Elapsed_Time.1']):>10}", file=f)
                print(f"- Moving Time: {s_to_hms(c_sum['Moving_Time']):>11}", file=f)
                print(f"- Distance: {c_sum['Distance.1']/1000:>11.2f} km", file=f)
                print(f"- Elevation: {c_sum['Elevation_Gain']:>11.2f} m", file=f)
                print(f"- Avg Speed: {p1:>8.2f} km/h", file=f)
                print(f"- Avg Speed: {p2:>13}", file=f)

                if not all_HR_missing: print(f"- Avg HR: {avg_bpm:>12.2f} bpm", file=f)

    #===============================================================================================================================
    # MONTHLY ANALYSIS
    #===============================================================================================================================

    def monthly_analysis(self, year, sport='All', output_dir='./res', threshold=0.0, with_figure=True):

        ## I) Extract specific dataframe

        # keep data from selected year in local dataframe
        df = self.df.loc[self.df['Activity_Date'].dt.year==year]

        # extract specific activities (sport type)
        if sport!='All': df = df.loc[df['Activity_Type'].astype(str)==sport]

        # compute number of filtered activities if distance threshold is given
        n0_filtered = df[df['Distance.1']<threshold].shape[0] if threshold>0.0 else 0

        # get total number of activities
        total_act = df.shape[0] - n0_filtered

        ## II) Perform monthly analysis

        # store monthly value in arrays
        data = np.zeros((4,12))

        # loop over sub-dataframe of each month
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        ## a. Write monthly analysis to txt file

        # create output folder if not existing
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        # set up output file path
        output_file = output_dir + '/' + str(year) + '_monthly_' + sport + '.txt'

        with open(output_file, 'w') as f:

            # if no activity found this year, abort analysis
            if total_act==0:

                print("\nNo activity found.", file=f)

            else:

                # loop over months
                for i, m in enumerate(months):

                    # get sub-dataframe of current month
                    df_i = df.loc[df['Activity_Date'].dt.month==i+1]

                    # get number of activities
                    n0 = df_i.shape[0]

                    # output header
                    print("\n---------- %s. ----------" %m, file=f)
                    print(f"\nActivities recorded: {n0:>5}", file=f)

                    if n0>0:

                        # filter activities if distance threshold is given
                        if threshold>0.0: df_i = df_i[df_i['Distance.1']>=threshold]

                        # update number of activities
                        n_act = df_i.shape[0]

                        # count number of filtered activities
                        n_filtered = n0 - n_act

                        # get number of activites with available HR data
                        n_act_HR = df_i['Average_Heart_Rate'].count()

                        # set flag if all activities of the year have missing HR data
                        all_HR_missing = True if n_act_HR==0 else False

                        # compute number of activites without HR data
                        n_act_no_HR = n_act - n_act_HR

                        # compute average bpm
                        if not all_HR_missing: avg_bpm = df_i['Average_Heart_Rate'].sum() / n_act_HR

                        # sum along columns for time, distance and elevation
                        c = ['Elapsed_Time.1', 'Moving_Time', 'Distance.1', 'Elevation_Gain']
                        c_sum = df_i[c].sum(axis=0)

                        # compute pace
                        p1, p2 = compute_pace(c_sum['Distance.1'], c_sum['Moving_Time'])

                        # append value in arrays
                        data[0,i] = c_sum['Moving_Time']
                        data[1,i] = c_sum['Distance.1']/1000
                        data[2,i] = c_sum['Elevation_Gain']
                        data[3,i] = p1

                        # outputs
                        print(f"Activities w/o HR: {n_act_no_HR:>7}", file=f)
                        print(f"Threshold: {threshold:>13.2f} m", file=f)
                        print(f"Activities filtered: {n_filtered:>5}", file=f)
                        print(f"\n- Elapsed Time: {s_to_hms(c_sum['Elapsed_Time.1']):>10}", file=f)
                        print(f"- Moving Time: {s_to_hms(c_sum['Moving_Time']):>11}", file=f)
                        print(f"- Distance: {data[1,i]:>11.2f} km", file=f)
                        print(f"- Elevation: {data[2,i]:>11.2f} m", file=f)
                        print(f"- Avg Speed: {p1:>8.2f} km/h", file=f)
                        print(f"- Avg Speed: {p2:>13}", file=f)

                        if not all_HR_missing: print(f"- Avg HR: {avg_bpm:>12.2f} bpm", file=f)

                # compute annual average from monthly data
                tot = data[:3,:].sum(axis=1)
                res = tot/12
                p = compute_pace(res[1]*1000, res[0])[0] if total_act>0 else 0.0

                print("\n**** AVERAGE P. MONTH ****\n", file=f)
                print(f"Avg Moving Time: {s_to_hms(res[0]):>9}", file=f)
                print(f"Avg Distance: {res[1]:>9.2f} km", file=f)
                print(f"Avg Elevation: {res[2]:>9.2f} m", file=f)
                print(f"Avg Speed: {p:>10.2f} km/h", file=f)

                ## b. Monthly histograms

                # check figure flag
                if with_figure:

                    # set up output file path
                    output_file = output_dir + '/' + str(year) + '_monthly_' + sport

                    # set ticks and labels
                    x_ticks = list(range(0,12))
                    m_names = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
                    ylabels = ["Moving Time [s]", "Distance [km]", "Elevation Gain [m]", "Average Pace [km/h]"]
                    filename = ['_time', '_dist', '_ele', '_pace']

                    # create histograms for each variable
                    for i in range(4):

                        plt.figure(figsize=(12,6))
                        plt.tick_params(axis='both', which='major', labelsize=12)
                        plt.title(str(year), fontweight='bold', fontsize=20)
                        plt.xlabel("Months", fontweight='bold', fontsize=14)
                        plt.ylabel(ylabels[i], fontweight='bold', fontsize=14)
                        plt.xticks(x_ticks, m_names)
                        plt.grid(zorder=0)
                        plt.bar(x_ticks, data[i], zorder=3)

                        # save current figure
                        plt.savefig(output_file+filename[i]+'.png', dpi=200)
