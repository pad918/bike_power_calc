from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_point import GpsDataPoint

#   Accounts for rolling resistance of wheels

class RollingForceModifyer(PowerModifyer): 

    # Mass of the bike + rider
    def __init__(self, cr, mass_kg):
        self._cr = cr
        self._mass_kg = mass_kg
        self._GRAVITATIONAL_CONSTANT = 9.8

    # Values used from: https://www.sheldonbrown.com/rinard/aero/formulas.html
    def modify_power_at_points(self, points):
        for p in points:
            force = self._cr * self._mass_kg * self._GRAVITATIONAL_CONSTANT
            rolling_power = force * p.speed
            p.power += rolling_power
