from gps_data.gps_data_loader import GPSDataLoader
from gps_data.gps_data_point import GpsDataPoint
import xml.etree.ElementTree as ET
import datetime
from geopy.distance import geodesic, great_circle

class GPXLoader(GPSDataLoader):

    def __init__(self, file_name):
        self.file_name = file_name        
        pass

    def load(self):
        # load file:
        GPX_NAMESPACE = {'gpx': 'http://www.topografix.com/GPX/1/1'}
        tree = ET.parse(self.file_name)
        xml_root = tree.getroot()
        trkpts = xml_root.findall('.//gpx:trkpt', GPX_NAMESPACE)
        points = []
        for trkpt in trkpts:
            lat = trkpt.get('lat')
            lon = trkpt.get('lon')
            ele = trkpt.find('gpx:ele', GPX_NAMESPACE).text
            time = trkpt.find('gpx:time', GPX_NAMESPACE).text

            # Convert to correct datatype
            lat = float(lat)
            lon = float(lon)
            ele = float(ele)
            time = datetime.datetime.fromisoformat(time)
            points.append(GpsDataPoint(lon, lat, ele, time, 0))

        # Update speed of all points
        for lp, np in zip(points[:-1], points[1:]):
            # Calculate avg speed between the two points
            dist_meters = geodesic((lp.latitude, lp.longitude), (np.latitude, np.longitude)).m
            delta_time:datetime.datetime = (np.time-lp.time).total_seconds()
            avg_speed = dist_meters / delta_time if delta_time>0 else 0
            lp.speed = avg_speed
        return points