# Generates simulated down-hill data with noise
#   Used to esimate precision and accuracy of the calibration script!



import argparse

import scipy.optimize
from gps_data.gpx_loader import GPXLoader
from gps_data import RawDataLoader
from gps_data.gps_data_points import GpsDataPoints
from gps_data.gps_data_point import GpsDataPoint

# Power modifyers
import power_modifyer as Power

# Filters
from gps_data import GpsDataFilter
from gps_data import GpsDataLowpassFilter

from typing import List
import plotly.graph_objects as go
import folium
import webbrowser
import numpy as np
import scipy
import math
import json


def get_power_points(points:GpsDataPoints, cwa, cr, mass, drivetrain_efficiency):
    points = points.clone()
    modifyers: List[Power.PowerModifyer] = [
        Power.AccelerationModifyer(mass),
        Power.ElevationModifyer(mass),
        Power.DragModifyer(cwa=cwa, use_weather_data=False),
        Power.RollingForceModifyer(cr=cr, mass_kg=mass),
    ]

    # Apply modifyers
    for modifyer in modifyers:
        modifyer.modify_power_at_points(points)

    return points

def meters_to_longitude(meters, latitude=0):
    METERS_PER_DEGREE_EQUATOR = 111319.49
    
    lat_radians = math.radians(latitude)
    
    delta_longitude = meters / (METERS_PER_DEGREE_EQUATOR * math.cos(lat_radians))
    
    return delta_longitude

# Solve for E
# E = mv²/2
# 2e = mv²
# 2e/m = v²
# v = sqrt(2e/m)

def get_new_vel(mass_kg:float, old_speed:float, energy_gain_j:float):
    def e(speed:float):
        return (mass_kg * speed**2) * 0.5
    def v_from_e(energy:float):
        return (2*energy/mass_kg) ** 0.5
    e_prev = e(old_speed)
    e_new = e_prev + energy_gain_j
    return v_from_e(e_new)

# One height per second
def generate_fake_data(heights:list[float]) -> GpsDataPoints:
    mass = 100
    cwa = 0.35
    cr = 0.004
    speed = 0
    gps_points = [GpsDataPoint(0, 0, heights[0], 0, speed)]
    drag_mod = Power.DragModifyer(cwa=cwa, use_weather_data=False)
    rolling_mod = Power.RollingForceModifyer(cr=cr, mass_kg=mass)
    distance_traveled = 0
    dt = 0.1
    for i in range(len(heights)-1):
        elevation_energy_gain = (heights[i]-heights[i+1])*mass*9.82
        speed = get_new_vel(mass, speed, elevation_energy_gain)
        distance_traveled += speed * dt
        new_point = GpsDataPoint(meters_to_longitude(distance_traveled), 0, heights[i+1], int((i+1)*1000*dt), speed)
        gps_points.append(new_point)
        power_gps_points = GpsDataPoints(gps_points[-2:])
        drag_mod.modify_power_at_points(power_gps_points)
        drag_power = power_gps_points.power[-1]
        power_gps_points = GpsDataPoints(gps_points[-2:])
        rolling_mod.modify_power_at_points(power_gps_points)
        rolling_power = power_gps_points.power[-1]
        speed = get_new_vel(mass, speed, -(rolling_power+drag_power)*dt)
        #print(f"""
#Elevation energy:   {elevation_energy_gain}
#Drag energy:        {drag_power*dt}
#Rolling energy:     {rolling_power*dt}""")
    
    return GpsDataPoints(gps_points[2::10])

def generate_raw_json(gps_data:GpsDataPoints):
    data = []
    for point in gps_data.get_points_list():
        data.append(
            {
                "longitude": float(point.longitude),
                "latitude": float(point.latitude),
                "altitude": float(point.altitude),
                "time": np.datetime_as_string(point.time, unit='ms'),
                "speed": float(point.speed)
            }
        )


    with open("test.json", "wt") as f:
        json.dump(data, f)

def get_heights1(seconds:int):
    def h_f(x:float):
        x*=0.1
        return 50.0 - math.log((x**2 + 0.8) / 0.001)
    return [h_f(float(x)) for x in range(seconds)]


def main():
    
    fake_data = generate_fake_data(get_heights1(200))
    print("SPEEDS: ", fake_data.speed)
    generate_raw_json(fake_data)
    pass


if __name__ == "__main__":
    main()

