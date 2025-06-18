import argparse
from gps_data.gpx_loader import GPXLoader
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

def create_power_map_folium(points:GpsDataPoints):
    if (len(points.power)==0):
        return
    
    center_latitide = np.average(points.latitude) 
    center_longitude = np.average(points.longitude) 
    m = folium.Map(location=[center_latitide, center_longitude], zoom_start=13, tiles='OpenStreetMap')
    folium.ColorLine(
        positions=list(zip(points.latitude, points.longitude)),
        colors=np.clip(points.speed, 0, 400), # Clip to make colors stand out more
        colormap=["b", "y", "r"],   
        weight=8,        
        opacity=0.7      
    ).add_to(m)

    output_html_file = "tmp.html"
    m.save(output_html_file)
    webbrowser.open(output_html_file)

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
    points = GpsDataPoints(GPXLoader(args.filename).load())

    # Apply filters to data
    filters: List[GpsDataFilter] = [
        GpsDataLowpassFilter()
    ]
    for filter in filters:
        filter.apply_filter(points=points)

    modifyers: List[Power.PowerModifyer] = [
        Power.AccelerationModifyer(args.mass),
        Power.ElevationModifyer(args.mass),
        Power.DragModifyer(cwa=0.6, use_weather_data=False),
        Power.RollingForceModifyer(cr=0.007, mass_kg=args.mass),
        Power.DragtrainEfficencyModifyer(efficency=args.drivetrain_efficiency) # MUST BE LAST
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
    avg_power = points.average_power()
    print(f"AVG power: {avg_power:.0f} w")
    
    #energy_joule = sum(max(0, l.power) * (n.time-l.time).total_seconds() for l, n in zip(points[:-1], points[1:]))
    energy_joule = np.sum(np.clip(points.power[:-1], 0, 10000) * ((points.time[1:]-points.time[:-1])/np.timedelta64(1, 's')))
    energy_kcal = energy_joule/4184
    muscle_energy_kcal = energy_kcal / 0.25
    print(f"Total burned energy: {muscle_energy_kcal:.0f} kcal")

    print(f"Total length: {(points.total_length()*1E-3):.2f}km")
    print(f"Total time: {points.total_time_hours():.2f}h")
    print(f"Avg speed: {(points.average_speed_kmph()):.2f}km/h")
    np.savetxt("saved.gz", np.maximum(points.power, 0))

if __name__ == "__main__":
    main()