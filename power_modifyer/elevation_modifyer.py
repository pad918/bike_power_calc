from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_point import GpsDataPoint


#   Power modifyer that takes into account for
#   elevation changes

class ElevationModifyer(PowerModifyer):

    

    # Mass of the bike + rider
    def __init__(self, mass_kg):
        self._mass_kg = mass_kg
        self._GRAVITATIONAL_CONSTANT = 9.8 # m/s^2

    def get_kinetic_energy_at_point(self, point:GpsDataPoint):
        return self._GRAVITATIONAL_CONSTANT * self._mass_kg * point.altitude

    def modify_power_at_points(self, points):
        for lp, np in zip(points[:-1], points[1:]):
            lp_energy = self.get_kinetic_energy_at_point(lp)
            np_energy = self.get_kinetic_energy_at_point(np)
            delta_energy = np_energy - lp_energy

            # Convert to avrage power
            time_delta = (np.time-lp.time).total_seconds()

            # Avg joules per second (Watts)
            avg_power = delta_energy / time_delta

            lp.power += avg_power