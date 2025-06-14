from abc import ABC
from abc import abstractmethod

# Abstract class for power modifyer

class PowerModifyer(ABC):
    
    def __init__(self):
        pass

    def modify_power_at_points(self, points):
        for point in points:
            self.modify_point_power(point)

    @abstractmethod
    def modify_point_power(self, point):
        pass