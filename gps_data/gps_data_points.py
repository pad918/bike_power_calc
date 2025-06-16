import numpy as np
from gps_data.gps_data_point import GpsDataPoint
from typing import List


# Class that holds multiple datapoints in numpy friendly way

class GpsDataPoints:

    def __init__(self, points: List[GpsDataPoint]):

        self.longitude = np.array([p.longitude for p in points])
        self.latitude = np.array([p.latitude for p in points])
        self.altitude = np.array([p.altitude for p in points])
        self.speed = np.array([p.speed for p in points])
        self.power = np.array([p.power for p in points], dtype='float64')
        self.time = np.array([p.time for p in points], dtype='datetime64[s]')

    def get_points_list(self):
        l = []
        for i in len(self.longitude):
            point = GpsDataPoint(
                self.longitude[i],
                self.latitude[i],
                self.altitude[i],
                self.time[i],
                self.speed[i]
            )
            point.power = self.power[i]
            l.append(point)
        return l
        
