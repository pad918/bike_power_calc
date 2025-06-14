from abc import ABC
from abc import abstractmethod

# Abstract class for power modifyer

class PowerModifyer(ABC):
    
    def __init__(self):
        pass
    
    @abstractmethod
    def modify_power_at_points(self, points):
        pass

