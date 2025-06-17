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
        self.time = np.array([p.time for p in points], dtype='datetime64[ms]')

    def clone(self):
        points = GpsDataPoints(self.get_points_list())
        return points

    def get_point(self, i):
        if i>= len(self.power):
            raise KeyError(f"Argument {i} is out of range")
        point = GpsDataPoint(
            self.longitude[i],
            self.latitude[i],
            self.altitude[i],
            self.time[i],
            self.speed[i],
        )
        point.power = self.power[i]
        return point
    
    def total_length(self):
        p_list = self.get_points_list()
        total_length = sum([p0.meter_distance_to(p1) for p1, p0 in zip(p_list[1:], p_list[:-1])])
        return total_length
    
    def total_time_hours(self):
        total_time = self.time[-1]-self.time[0]
        total_time_hours = total_time / np.timedelta64(1, 'h')
        return total_time_hours
    
    def average_speed_kmph(self):
        return (self.total_length()*1E-3/self.total_time_hours())

    def average_power(self):
        p_list = self.get_points_list()
        power_seconds = np.sum([p0.power * ((p1.time-p0.time) / np.timedelta64(1, "s"))  for p1, p0 in zip(p_list[1:], p_list[:-1])])
        total_seconds = (p_list[-1].time - p_list[0].time) / np.timedelta64(1, "s")
        avg_power = power_seconds / total_seconds
        return avg_power

    def get_points_list(self):
        l = []
        for i in range(len(self.longitude)):
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
        
