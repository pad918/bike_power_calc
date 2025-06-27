from gps_data.gps_data_loader import GPSDataLoader
from gps_data.gps_data_point import GpsDataPoint
import datetime
import json


class RawDataLoader(GPSDataLoader):

    def __init__(self, file_name):
        self.file_name = file_name        
        pass

    def load(self):
        with open(self.file_name, "rt") as f:
            gps_json_data = json.load(f)
        
        points = []
        for data_point in gps_json_data:
            datetime_time = datetime.datetime.fromisoformat(data_point["time"])
            point = GpsDataPoint(
                data_point["longitude"],
                data_point["latitude"],
                data_point["altitude"],
                datetime_time,
                data_point["speed"]
            )
            points.append(point)


        return points