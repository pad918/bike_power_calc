import argparse
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

def create_and_open_power_map_folium(points:GpsDataPoints):
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

def get_total_burned_energy_kcal(dataPoints:GpsDataPoints, muscleEfficiency:float) -> float:
    energy_joule = np.sum(np.clip(dataPoints.power[:-1], 0, 10000) * ((dataPoints.time[1:]-dataPoints.time[:-1])/np.timedelta64(1, 's')))
    energy_kcal = energy_joule/4184
    muscle_energy_kcal = energy_kcal / muscleEfficiency
    return muscle_energy_kcal

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("filename", help="File to load datapoints from")
    arg_parser.add_argument("mass", help="Total mass of the bike + rider in kg", type=float)
    arg_parser.add_argument("--drivetrain_efficiency", 
                            help="Efficency of the drivetrain, typicall 0.95", 
                            type=float,
                            default=0.95,
                            required=False)
    arg_parser.add_argument("--muscle_efficency", 
                            help="Total muscle efficiency. Default 20%", 
                            type=float,
                            default=0.2,
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

    modifyers: List[Power.PowerModifyer] = [
        Power.AccelerationModifyer(args.mass),
        Power.ElevationModifyer(args.mass),
        Power.DragModifyer(cwa=0.56370, use_weather_data=False), #0.56370, cr: 0.00356
        Power.RollingForceModifyer(cr=0.00356, mass_kg=args.mass),
        Power.DragtrainEfficencyModifyer(efficency=args.drivetrain_efficiency) # MUST BE LAST
    ]

    # Apply modifyers
    for modifyer in modifyers:
        modifyer.modify_power_at_points(points)


    # Calculate and print stats
    avg_power = points.average_power()
    
    
    muscle_energy_kcal = get_total_burned_energy_kcal(points, args.muscle_efficency)
    print(f"""
===================== STATS =====================
|    Total burned energy: {muscle_energy_kcal:.0f} kcal
|    Total distance:      {(points.total_length()*1E-3):.2f} km
|    Total time:          {points.total_time_hours():.2f} h
|    Avg speed:           {(points.average_speed_kmph()):.2f} km/h
|    AVG power:           {avg_power:.0f} w
=================================================
""")

    np.savetxt("saved.gz", np.maximum(points.power, 0))

    # Draw graphs
    fig = go.Figure(data=[
        go.Scatter(
            x=points.time, 
            y=np.maximum(points.power, 0))
            ]
        )
    fig.show()

    create_and_open_power_map_folium(points=points)

if __name__ == "__main__":
    main()