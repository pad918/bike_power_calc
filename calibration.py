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
    points.upsample(target_hz=10)

    # Apply filters to data
    filters: List[GpsDataFilter] = [
        GpsDataLowpassFilter()
    ]
    for filter in filters:
        filter.apply_filter(points=points)

    def opt(cwa_cr):
        cwa, cr = cwa_cr
        p = get_power_points(points, cwa, cr, args.mass, args.drivetrain_efficiency)
        powers:np.array = p.power[:-2]
        return np.sum(np.abs(powers))

    # Find cwa and cr with scipy
    result = scipy.optimize.minimize(fun=opt, x0=np.array([0.6, 0.007]), method='Nelder-Mead')
    if(not result.success):
        print("Could not find coefficiants...")
        raise BaseException("Bad input data")
    
    print(f"Found following valus: cwa: {result.x[0]:.5f}, cr: {result.x[1]:.5f}, error: {(result.fun / len(points.power))**0.5}")

    # AI VISUALIZATION
    
    # 1. Calculate the final power points using the optimized coefficients
    optimal_cwa, optimal_cr = result.x
    final_points = get_power_points(points, optimal_cwa, optimal_cr, args.mass, args.drivetrain_efficiency)
    
    # 2. Create the graph
    fig = go.Figure()

    # Plot the residual power
    fig.add_trace(go.Scatter(
        y=final_points.power, 
        mode='lines', 
        name='Residual Power',
        line=dict(color='blue')
    ))

    # Add a horizontal line at y=0 (The target)
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_color="red", 
        annotation_text="Target (0 Watts)", 
        annotation_position="bottom right"
    )

    # Layout styling
    fig.update_layout(
        title="Optimized Residual Power Over Track",
        xaxis_title="Data Point Index",
        yaxis_title="Power Difference (Watts)",
        template="plotly_white",
        hovermode="x unified"
    )

    # 3. Open the graph in the default web browser
    fig.show()

if __name__ == "__main__":
    main()