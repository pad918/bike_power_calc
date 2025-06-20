from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_points import GpsDataPoints
import numpy as np
#   Accounts for rolling resistance of wheels

class RollingForceModifyer(PowerModifyer): 

    # Mass of the bike + rider
    def __init__(self, cr, mass_kg):
        self._cr = cr
        self._mass_kg = mass_kg
        self._GRAVITATIONAL_CONSTANT = 9.8

    # Values used from: https://www.sheldonbrown.com/rinard/aero/formulas.html
    def modify_power_at_points(self, points:GpsDataPoints):
        force = self._cr * self._mass_kg * self._GRAVITATIONAL_CONSTANT
        rolling_powers = force * points.speed
        points.power += rolling_powers
