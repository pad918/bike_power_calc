import argparse
from gps_data.gpx_loader import GPXLoader

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


def create_power_map_folium(points):
    m = folium.Map(location=[points[0].latitude, points[0].longitude], zoom_start=15, tiles='OpenStreetMap')
    folium.ColorLine(
        positions=[(p.latitude, p.longitude) for p in points],
        colors=[p.power if p.power>0 else 0 for p in points],
        colormap=["b", "y", "r"],   
        weight=5,        
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
    points = GPXLoader(args.filename).load()
    
    # Apply filters to data
    filters: List[GpsDataFilter] = [
        GpsDataLowpassFilter()
    ]
    for filter in filters:
        filter.apply_filter(points=points)


    modifyers: List[PowerModifyer] = [
        AccelerationModifyer(args.mass),
        ElevationModifyer(args.mass),
        DragModifyer(cwa=0.6),
        RollingForceModifyer(cr=0.007, mass_kg=args.mass),
        DragtrainEfficencyModifyer(efficency=args.drivetrain_efficiency) # MUST BE LAST
    ]

    # Apply modifyers
    for modifyer in modifyers:
        modifyer.modify_power_at_points(points)

    # Draw graph
    fig = go.Figure(data=[
        go.Scatter(
            x=[p.time for p in points], 
            y=[p.power for p in points])
            ]
        )
    fig.show()

    ### DRAW MAP
    create_power_map_folium(points=points)

    avg_power = sum([p.power if p.power>0 else 0 for p in points])/len(points)
    print(f"AVG power: {avg_power}w")

    # Total burened energy
    energy = 0
    for l, n in zip(points[:-1], points[1:]):
        if(not l.power>0):
            continue
        e = l.power * 2
        energy += e
    energy /= 4200
    print(f"Total burned energy: {energy} kcal")


if __name__ == "__main__":
    main()