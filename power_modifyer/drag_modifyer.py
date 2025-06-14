from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_point import GpsDataPoint


#   Power modifyer that takes into account for
#   elevation changes

class DragModifyer(PowerModifyer): 

    # Mass of the bike + rider
    def __init__(self, cwa):
        self._cwa = cwa
        pass

    # Values used from: https://www.sheldonbrown.com/rinard/aero/formulas.html
    def modify_power_at_points(self, points):
        for p in points:
            r = 1.2 # kg/m3
            wind_v = p.speed # Assume no wind
            drag_force = r*self._cwa*wind_v**2*0.5
            drag_power = drag_force * p.speed
            p.power += drag_power
