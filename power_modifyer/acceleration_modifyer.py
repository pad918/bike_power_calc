from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_points import GpsDataPoints
import datetime
import numpy as np

#   Power modifyer that takes into account
#   the power needed to accelerate between 
#   points 

class AccelerationModifyer(PowerModifyer):

    # Mass of the bike + rider
    def __init__(self, mass_kg):
        self._mass_kg = mass_kg

    def get_kinetic_energy_at_speed(self, speed_mps):
        return 0.5 * self._mass_kg * speed_mps**2

    def modify_power_at_points(self, points:GpsDataPoints):
        energies = 0.5 * self._mass_kg * points.speed**2
        delta_energies = energies[1:] - energies[:-1]
        delta_times = points.time[1:] - points.time[:-1]
        delta_time_seconds = delta_times / np.timedelta64(1, 's')
        powers = delta_energies / np.maximum(delta_time_seconds, 1)
        # Add the power needed at each point
        points.power[:-1] += powers 