from abc import ABC, abstractmethod

class GPSDataLoader(ABC):

    @abstractmethod
    def load(self):
        pass
    