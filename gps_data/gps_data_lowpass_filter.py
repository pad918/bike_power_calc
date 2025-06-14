from gps_data.data_filter import GpsDataFilter
import numpy as np

#   Filter that applies a lowpass filter
#   to elevation and speed data
#

class GpsDataLowpassFilter(GpsDataFilter):

    def __init__(self):
        pass

    def apply_filter(self, points):
        # Use kernel lowpass filter (blur)
        kernel = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
        n = len(kernel)
        speeds = np.array([p.speed for p in points])
        elevations = np.array([p.altitude for p in points])
        
        # Apply the kernel
        filtered_speeds = np.convolve(speeds, kernel, mode='same')
        filtered_elevations = np.convolve(elevations, kernel, mode='same')

        # Update the values
        for p, s, e in zip(points[n:-n], filtered_speeds[n:-n], filtered_elevations[n:-n]):
            p.speed = s
            p.altitude = e