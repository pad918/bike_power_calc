import argparse
from gps_data.gpx_loader import GPXLoader
from gps_data.gps_data_points import GpsDataPoints

# Power modifyers
from power_modifyer.power_modifyer import PowerModifyer
from power_modifyer.acceleration_modifyer import AccelerationModifyer
from power_modifyer.elevation_modifyer import ElevationModifyer
from power_modifyer.drag_modifyer import DragModifyer
from power_modifyer.rolling_force_modifyer import RollingForceModifyer
from power_modifyer.drivetrain_efficency_modifyer import DragtrainEfficencyModifyer

# Filters
from gps_data.data_filter import GpsDataFilter
from gps_data.gps_data_lowpass_filter import GpsDataLowpassFilter

from typing import List
import plotly.graph_objects as go
import folium
import webbrowser
import numpy as np

def create_power_map_folium(points:GpsDataPoints):
    if (len(points.power)==0):
        return
    
    center_latitide = np.average(points.latitude) 
    center_longitude = np.average(points.longitude) 
    m = folium.Map(location=[center_latitide, center_longitude], zoom_start=13, tiles='OpenStreetMap')
    folium.ColorLine(
        positions=list(zip(points.latitude, points.longitude)),
        colors=np.clip(points.power, 0, 400), # Clip to make colors stand out more
        colormap=["b", "y", "r"],   
        weight=8,        
        opacity=0.7      
    ).add_to(m)

    output_html_file = "tmp.html"
    m.save(output_html_file)
    webbrowser.open(output_html_file)

def main():
    import sys
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
    points = GpsDataPoints(GPXLoader(args.filename).load())

    # Apply filters to data
    filters: List[GpsDataFilter] = [
        GpsDataLowpassFilter()
    ]
    for filter in filters:
        filter.apply_filter(points=points)

    modifyers: List[PowerModifyer] = [
        AccelerationModifyer(args.mass),
        ElevationModifyer(args.mass),
        DragModifyer(cwa=0.6, use_weather_data=False),
        RollingForceModifyer(cr=0.007, mass_kg=args.mass),
        DragtrainEfficencyModifyer(efficency=args.drivetrain_efficiency) # MUST BE LAST
    ]

    # Apply modifyers
    for modifyer in modifyers:
        modifyer.modify_power_at_points(points)

    # Draw graphs
    fig = go.Figure(data=[
        go.Scatter(
            x=points.time, 
            y=np.maximum(points.power, 0))
            ]
        )
    fig.show()

    create_power_map_folium(points=points)

    # Calculate and print stats
    avg_power = np.average(np.maximum(points.power, 0))
    print(f"AVG power: {avg_power:.0f} w")
    
    #energy_joule = sum(max(0, l.power) * (n.time-l.time).total_seconds() for l, n in zip(points[:-1], points[1:]))
    energy_joule = np.sum(np.clip(points.power[:-1], 0, 10000) * ((points.time[1:]-points.time[:-1])/np.timedelta64(1, 's')))
    energy_kcal = energy_joule/4184
    print(f"Total burned energy: {energy_kcal:.0f} kcal")


if __name__ == "__main__":
    main()