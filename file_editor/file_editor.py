#!/usr/bin/env python3

#===================================================================================================================================
# CONSTANTS
#===================================================================================================================================

# Earth radius (in meters)
R = 6371000

#===================================================================================================================================
# LIBRARIES
#===================================================================================================================================

import os, sys, time
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

    def __init__(self, file_path):

        # read file
        if os.path.exists(file_path):

            self.path = file_path
            self.read_file()

        else:

            raise FileNotFoundError("No such file or directory: "+repr(file_path))

    #===============================================================================================================================
    # GENERIC READ
    #===============================================================================================================================

    def read_file(self):

        tree = ET.parse(self.path)
        self.root = tree.getroot()

        if self.path.endswith('.gpx'):

            self.namespace = {
                'gpx'      : 'http://www.topografix.com/GPX/1/1',
                'gpxtpx'   : 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1',
                'gpxx'     : 'http://www.garmin.com/xmlschemas/GpxExtensions/v3'
            }

            self.read_gpx()

        elif self.path.endswith('.tcx'):

            self.namespace = {
                'tcx'   : 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
                'ns3'   : "http://www.garmin.com/xmlschemas/ActivityExtension/v2"
            }

            self.read_tcx()

        else:

            raise TypeError("Unsupported file format. Should be either GPX or TCX.")

    #===============================================================================================================================
    # READ XML ELEMENT
    #===============================================================================================================================

    def __findChildTag__(self, element, tag, tofloat=True, default=None):

        # search child with tag
        res = element.find(tag, self.namespace)

        # default return
        if res is None:

            return default

        # else handle tag case
        else:

            return float(res.text) if tofloat else res.text

    def __getAttribute__(self, element, tag, tofloat=True, default=None):

        # get attribute of current element
        res = element.get(tag)

        # default return
        if res is None:

            return default

        # else handle tag case
        else:

            return float(res) if tofloat else res

    #===============================================================================================================================
    # READ GPX FILE
    #===============================================================================================================================

    def read_gpx( self ):

        # 1. Parse metadata

        # activity type
        self.sport = self.__findChildTag__(element=self.root, tag='.//gpx:type', tofloat=False, default='Unknown')

        # start time
        self.start_time = self.__findChildTag__(element=self.root, tag='.//gpx:metadata/gpx:time', tofloat=False, default='Unknown')

        # total activity time
        self.total_time = 0.0

        # total activity distance
        self.total_dist = 0.0

        # calories
        self.calories = 0.0

        # avg bpm
        self.avg_bpm = 0.0

        # max bpm
        self.max_bpm = 0.0

        # device
        self.device = 'Unknown'

        # 2. Parse trackpoints

        # initialize empty data matrix
        data  = []

        # iterate through each trackpoint
        for trackpoint in self.root.findall('.//gpx:trkseg/gpx:trkpt', self.namespace):

            # time
            time = self.__findChildTag__(element=trackpoint, tag='./gpx:time', tofloat=False)

            # position
            lat = self.__getAttribute__(element=trackpoint, tag='lat')
            lon = self.__getAttribute__(element=trackpoint, tag='lon')

            # elevation
            ele = self.__findChildTag__(element=trackpoint, tag='./gpx:ele')

            # distance
            dist = 0.0 #self.__findChildTag__(element=trackpoint, tag='gpx:dist')

            # bpm
            bpm = self.__findChildTag__(element=trackpoint, tag='.//gpxtpx:hr')

            # append data to matrix
            data.append([time, lat, lon, ele, dist, bpm])

        self.data = np.array(data, dtype=object)

    #===============================================================================================================================
    # READ TCX FILE
    #===============================================================================================================================
    
    def read_tcx( self ):

        # 1. Parse metadata

        # activity type
        activity = self.root.find('.//tcx:Activity', self.namespace)
        self.sport = self.__getAttribute__(element=activity, tag='Sport', tofloat=False, default='Unknown')

        # start time
        self.start_time = self.__findChildTag__(element=self.root, tag='.//tcx:Id', tofloat=False, default='Unknown')

        # total activity time
        self.start_time = self.__findChildTag__(element=self.root, tag='.//tcx:TotalTimeSeconds', default=0.0)

        # total activity distance
        self.total_dist = self.__findChildTag__(element=self.root, tag='.//tcx:DistanceMeters', default=0.0)

        # calories
        self.calories = self.__findChildTag__(element=self.root, tag='.//tcx:Calories', default=0.0)

        # avg bpm
        self.avg_bpm = self.__findChildTag__(element=self.root, tag='.//tcx:AverageHeartRateBpm/tcx:Value', default=0.0)

        # max bpm
        self.max_bpm = self.__findChildTag__(element=self.root, tag='.//tcx:MaximumHeartRateBpm/tcx:Value', default=0.0)

        # device
        self.device = self.__findChildTag__(element=self.root, tag='.//tcx:Creator/tcx:Name', tofloat=False, default='Unknown')

        # 2. Parse trackpoints

        # initialize empty data matrix
        data  = []

        # iterate through each trackpoint
        for trackpoint in self.root.findall('.//tcx:Track/tcx:Trackpoint', self.namespace):

            # time
            time = self.__findChildTag__(element=trackpoint, tag='./tcx:Time', tofloat=False)

            # position
            lat = self.__findChildTag__(element=trackpoint, tag='./tcx:Position/tcx:LatitudeDegrees')
            lon = self.__findChildTag__(element=trackpoint, tag='./tcx:Position/tcx:LongitudeDegrees')

            # elevation
            ele = self.__findChildTag__(element=trackpoint, tag='./tcx:AltitudeMeters')

            # distance
            dist = self.__findChildTag__(element=trackpoint, tag='./tcx:DistanceMeters')

            # bpm
            bpm = self.__findChildTag__(element=trackpoint, tag='./tcx:HeartRateBpm/tcx:Value')

            # append data to matrix
            data.append([time, lat, lon, ele, dist, bpm])

        self.data = np.array(data, dtype=object)

    #===============================================================================================================================
    # SUMMARIZE FILE
    #===============================================================================================================================

    def summarize(self):

        print("\n"+15*"==="+"\n"+self.path.center(45)+"\n"+15*"==="+"\n")

        # print class attributes
        print(15*"---"+"\n"+"METADATA".center(45)+"\n"+15*"---")

        for key, value in self.__dict__.items():
            if key not in ['path','namespace','root','data']:
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
