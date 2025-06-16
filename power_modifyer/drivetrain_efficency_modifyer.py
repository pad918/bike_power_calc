from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_points import GpsDataPoints


#   Power modifyer that takes into account for
#   elevation changes

class DragtrainEfficencyModifyer(PowerModifyer): 

    # Mass of the bike + rider
    def __init__(self, efficency=0.95):
        self._drivetrain_efficency = efficency

    def modify_power_at_points(self, points:GpsDataPoints):
        mask_positive = points.power > 0
        points.power[mask_positive] /= self._drivetrain_efficency
