from abc import ABC, abstractmethod

class Optimizer(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def optimize_power_curve(self, points, avg_power):
        pass