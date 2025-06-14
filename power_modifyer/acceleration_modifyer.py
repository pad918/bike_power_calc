from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_point import GpsDataPoint
import datetime

#   Power modifyer that takes into account
#   the power needed to accelerate between 
#   points 

class AccelerationModifyer(PowerModifyer):

    # Mass of the bike + rider
    def __init__(self, mass_kg):
        self._mass_kg = mass_kg

    def get_kinetic_energy_at_speed(self, speed_mps):
        return 0.5 * self._mass_kg * speed_mps**2

    def modify_power_at_points(self, points):
        for lp, np in zip(points[:-1], points[1:]):
            lp_energy = self.get_kinetic_energy_at_speed(lp.speed)
            np_energy = self.get_kinetic_energy_at_speed(np.speed)
            delta_energy = np_energy - lp_energy

            # Convert to avrage power
            time_delta = (np.time-lp.time).total_seconds()

            # Avg joules per second (Watts)
            avg_power = delta_energy / time_delta

            lp.power += avg_power