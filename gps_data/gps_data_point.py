from helpers.ranges import OpenRange
import datetime
from geopy.distance import geodesic, great_circle
from geopy.point import Point

class GpsDataPoint:
    
    def __init__(self, longitude, latitude, altitude, time, speed):
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.speed = speed
        self.time = time
        self.power = 0

    def meter_distance_to(self, other):
        return geodesic((self.latitude, self.longitude), (other.latitude, other.longitude)).m

    def get_bearing_to(self, other):
        p1 = Point(self.latitude, self.longitude)
        p2 = Point(other.latitude, other.longitude)
        return geodesic(p1, p2).initial_bearing
    
    # Define getters / setters
    @property
    def longitude(self):
        return self._longitude
    
    @longitude.setter
    def longitude(self, val):
        if(not val in OpenRange(-180, 180)):
            raise BaseException(f"Invalid longitude {val}")
        self._longitude = val
    
    @property
    def latitude(self):
        return self._latitude
    
    @latitude.setter
    def latitude(self, val):
        if(not val in OpenRange(-90, 90)):
            raise BaseException(f"Invalid latitude: {val}")
        self._latitude = val
        
    @property
    def altitude(self):
        return self._altitude
    
    @altitude.setter
    def altitude(self, val):
        if(not val in OpenRange(-100, 8000)):
            raise BaseException(f"The altitude is most likely incorrect: {val}m")
        self._altitude = val

    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, val):
        if(not val in OpenRange(-30, 30)):
            raise BaseException(f"Speed must be in m/s, {val} is most likely an other using another unit")
        self._speed = val

    @property
    def time(self):
        return self._time
    
    @time.setter
    def time(self, val):
        if(not type(val) == datetime.datetime):
            raise BaseException(f"Can only set time to time type, not: {type(val)}")
        self._time = val

    @property
    def power(self):
        return self._power
    
    @power.setter
    def power(self, val):
        self._power = val