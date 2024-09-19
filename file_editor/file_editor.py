#!/usr/bin/env python3

#===================================================================================================================================
# CONSTANTS
#===================================================================================================================================

# Earth radius (in meters)
R = 6371000

#===================================================================================================================================
# LIBRARIES
#===================================================================================================================================

import os , sys , errno , re , time
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

sys.tracebacklimit = 0

#===================================================================================================================================
# CLASS ACTIVITY
#===================================================================================================================================

class activity:

    #===============================================================================================================================
    # INIT
    #===============================================================================================================================

    def __init__( self , file_path ):

        # default attributes
        self.sport          = 'Unknown'
        self.start_time     = 'Unknown'
        self.total_time     = -1
        self.total_dist     = -1
        self.calories       = -1
        self.avg_bpm        = -1
        self.max_bpm        = -1
        self.device         = 'Unknown'

        # read file
        if os.path.exists( file_path ):

            self.path = file_path
            self.read_file()

        else:

            raise FileNotFoundError( "No such file or directory: " + repr(file_path) )

    #===============================================================================================================================
    # GENERIC READ
    #===============================================================================================================================

    def read_file( self ):

        tree = ET.parse( self.path )
        root = tree.getroot()

        if self.path.endswith('.gpx'):

            namespace = None

            self.read_gpx( root , namespace )

        elif self.path.endswith('.tcx'):

            namespace = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}

            self.read_tcx( root , namespace )

        else:

            raise TypeError( "Unsupported file format. Should be either GPX or TCX." )

    #===============================================================================================================================
    # READ GPX FILE
    #===============================================================================================================================

    def read_gpx( self , root ):

        #TODO
        None

    #===============================================================================================================================
    # READ TCX FILE
    #===============================================================================================================================
    
    def read_tcx( self , root , namespace ):

        # 1. Parse metadata

        # activity type
        res = root.find('.//tcx:Activity', namespace)
        self.sport = res.attrib.get('Sport', 'Unknown')

        # start time
        res = root.find('.//tcx:Id', namespace)
        if res is not None: self.start_time = res.text 

        # total activity time
        res = root.find('.//tcx:TotalTimeSeconds', namespace)
        if res is not None: self.total_time = float(res.text)

        # total activity distance
        res = root.find('.//tcx:DistanceMeters', namespace)
        if res is not None: self.total_dist = float(res.text)

        # calories
        res = root.find('.//tcx:Calories', namespace)
        if res is not None: self.calories = float(res.text)

        # avg bpm
        tmp = root.find('.//tcx:AverageHeartRateBpm', namespace)
        if tmp is not None: res = tmp.find('tcx:Value', namespace)
        if res is not None: self.avg_bpm = float(res.text)

        # max bpm
        tmp = root.find('.//tcx:MaximumHeartRateBpm', namespace)
        if tmp is not None: res = tmp.find('tcx:Value', namespace)
        if res is not None: self.max_bpm = float(res.text)

        # device
        tmp = root.find('.//tcx:Creator', namespace)
        if tmp is not None: res = tmp.find('tcx:Name', namespace)
        if res is not None: self.device = res.text

        # 2. Parse trackpoints

        # initialize empty data matrix
        data  = []

        # iterate through each trackpoint
        for track in root.findall('.//tcx:Track', namespace):
            for trackpoint in track.findall('tcx:Trackpoint', namespace):

                # time
                res = trackpoint.find('tcx:Time', namespace)
                time = res.text if res is not None else None

                # position
                res = trackpoint.find('tcx:Position/tcx:LatitudeDegrees', namespace)
                lat = float(res.text) if res is not None else None
                res = trackpoint.find('tcx:Position/tcx:LongitudeDegrees', namespace)
                lon = float(res.text) if res is not None else None

                # elevation
                res = trackpoint.find('tcx:AltitudeMeters', namespace)
                ele = float(res.text) if res is not None else None

                # distance
                res = trackpoint.find('tcx:DistanceMeters', namespace)
                dist = float(res.text) if res is not None else None

                # bpm
                res = trackpoint.find('tcx:HeartRateBpm/tcx:Value', namespace)
                bpm = float(res.text) if res is not None else None

                # append data to matrix
                data.append([time, lat, lon, ele, dist, bpm])

        self.data = np.array(data, dtype=object)

    #===============================================================================================================================
    # SUMMARIZE FILE
    #===============================================================================================================================

    def summarize( self ):

        print("\n"+15*"==="+"\n"+self.path.center(45)+"\n"+15*"==="+"\n")

        # print class attributes except path or data matrix
        print(15*"---"+"\n"+"METADATA".center(45)+"\n"+15*"---")

        for key, value in self.__dict__.items():
            if key not in ['path','data']:
                print(f"{key.ljust(12)}: {value}")

        # print additional information about data
        print(15*"---"+"\n"+"TRACK DATA".center(45)+"\n"+15*"---")

        n = self.data.shape[0]

        print(f"{'trackpoints'.ljust(12)}: {n}")

        if n>2:

            print(f"{'with time'.ljust(12)}: {self.data[0,0] is not None}")
            print(f"{'with coord'.ljust(12)}: {self.data[0,1] is not None and self.data[0,2] is not None}")
            print(f"{'with ele'.ljust(12)}: {self.data[0,3] is not None}")
            print(f"{'with dist'.ljust(12)}: {self.data[1,4]>0.0}")
            print(f"{'with bpm'.ljust(12)}: {self.data[0,5] is not None}")
