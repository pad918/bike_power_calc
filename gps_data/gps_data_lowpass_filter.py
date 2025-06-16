from gps_data.data_filter import GpsDataFilter
from gps_data.gps_data_points import GpsDataPoints
import numpy as np

#   Filter that applies a lowpass filter
#   to elevation and speed data
#

class GpsDataLowpassFilter(GpsDataFilter):

    def __init__(self):
        pass

    def apply_filter(self, points:GpsDataPoints):
        # Use kernel lowpass filter (blur)
        kernel = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
        n = len(kernel)
        
        # Apply the kernel
        filtered_speeds = np.convolve(points.speed, kernel, mode='same')
        filtered_elevations = np.convolve(points.altitude, kernel, mode='same')

        # Update the values
        points.speed[n:-n] = filtered_speeds[n:-n]
        points.altitude[n:-n] = filtered_elevations[n:-n]
