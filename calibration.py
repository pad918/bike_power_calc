# A script that calculates the bike's coeficients from a track

import argparse

import scipy.optimize
from gps_data.gpx_loader import GPXLoader
from gps_data import RawDataLoader
from gps_data.gps_data_points import GpsDataPoints

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

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("filename", help="File to load datapoints from")
    arg_parser.add_argument("mass", help="Total mass of the bike + rider in kg", type=float)
    arg_parser.add_argument("--drivetrain_efficiency", 
                            help="Efficency of the drivetrain, typicall 0.95", 
                            type=float,
                            default=0.95,
                            required=False)
    args = arg_parser.parse_args()

    # Load gps data
    file_extension = args.filename.split(".")[-1] 
    if(file_extension == "gpx"):
        loader = GPXLoader(args.filename)
    elif(file_extension == "json"):
        loader = RawDataLoader(args.filename)
    points = GpsDataPoints(loader.load())

    # Apply filters to data
    filters: List[GpsDataFilter] = [
        GpsDataLowpassFilter()
    ]
    for filter in filters:
        filter.apply_filter(points=points)

    def opt(cwa_cr):
        cwa, cr = cwa_cr
        p = get_power_points(points, cwa, cr, args.mass, args.drivetrain_efficiency)
        powers:np.array = p.power
        return np.sum(powers**2)

    # Find cwa and cr with scipy
    result = scipy.optimize.minimize(fun=opt, x0=np.array([0.6, 0.007]), method='Nelder-Mead')
    if(not result.success):
        print("Could not find coefficiants...")
        raise BaseException("Bad input data")
    
    print(f"Found following valus: cwa: {result.x[0]:.5f}, cr: {result.x[1]:.5f}, error: {(result.fun / len(points.power))**0.5}")

if __name__ == "__main__":
    main()