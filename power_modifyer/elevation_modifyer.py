from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_points import GpsDataPoints
import numpy as np

#   Power modifyer that takes into account for
#   elevation changes

class ElevationModifyer(PowerModifyer):

    # Mass of the bike + rider
    def __init__(self, mass_kg):
        self._mass_kg = mass_kg
        self._GRAVITATIONAL_CONSTANT = 9.8 # m/s^2

    def get_kinetic_energy_at_point(self, point:GpsDataPoints):
        return self._GRAVITATIONAL_CONSTANT * self._mass_kg * point.altitude

    def modify_power_at_points(self, points:GpsDataPoints):
        gravitational_energies = self._GRAVITATIONAL_CONSTANT * self._mass_kg * points.altitude
        delta_energies =  gravitational_energies[1:] - gravitational_energies[:-1]
        delta_times = points.time[1:] - points.time[:-1]
        delta_time_seconds = delta_times / np.timedelta64(1, 's')
        powers = delta_energies / np.maximum(delta_time_seconds, 1)
        
        # Add the power needed at each point
        points.power[:-1] += powers 