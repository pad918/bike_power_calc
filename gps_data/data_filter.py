from abc import ABC, abstractmethod

# ABC for data filters

class GpsDataFilter(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def apply_filter(self, points):
        pass
