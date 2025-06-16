from power_modifyer.power_modifyer import PowerModifyer
from gps_data.gps_data_point import GpsDataPoint
from meteostat import Point, Hourly
from pytz import timezone
import datetime

#   Power modifyer that takes into account for
#   elevation changes

class DragModifyer(PowerModifyer): 

    # Mass of the bike + rider
    def __init__(self, cwa, use_weather_data=False):
        self._cwa = cwa
        self._use_weather_data = use_weather_data

    # Values used from: https://www.sheldonbrown.com/rinard/aero/formulas.html
    def modify_power_at_points(self, points):
        # Assumes that the weather was constant during the trip, TODO fix this

        # Get wind data
        if(self._use_weather_data):
            location = Point(points[0].latitude, points[0].longitude, points[0].altitude)
            start:datetime.datetime = points[0].time
            
            
            # meteostat needs the datetimes to be pure dates, with no hour, minute and second info...
            start = datetime.datetime(
                year=start.year, 
                month=start.month,
                day=start.day,
                hour=start.hour)
            
            end:datetime.datetime = start + datetime.timedelta(hours=0)
            # temp', 'dwpt', 'rhum', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun', 'coco'
            print(start.isoformat())
            print(end.isoformat())
            daily_data = Hourly(location, start=start, end=end)
            data = daily_data.fetch()
            print(data)

            wind_angle = data["wdir"][0]
            wind_avg_speed_kmph = data["wspd"][0]
            wing_avg_speed_mps = wind_avg_speed_kmph / 3.6
        
        # Apply modifyer
        r = 1.2 # kg/m3
        wind_v = points.speed # Assume no wind
        drag_force = r*self._cwa*wind_v**2*0.5
        drag_power = drag_force * points.speed
        points.power += drag_power
