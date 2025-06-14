from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_point import GpsDataPoint


#   Power modifyer that takes into account for
#   elevation changes

class DragtrainEfficencyModifyer(PowerModifyer): 

    # Mass of the bike + rider
    def __init__(self, efficency=0.95):
        self._drivetrain_efficency = efficency

    def modify_power_at_points(self, points):
        for p in points:
            if(p.power > 0):
                p.power /= self._drivetrain_efficency
