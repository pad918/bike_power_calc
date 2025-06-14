import argparse
import sys
from gps_data.gpx_loader import GPXLoader

# Power modifyers
from power_modifyer.power_modifyer import PowerModifyer
from power_modifyer.acceleration_modifyer import AccelerationModifyer
from power_modifyer.elevation_modifyer import ElevationModifyer
from power_modifyer.drag_modifyer import DragModifyer

# Filters
from gps_data.data_filter import GpsDataFilter
from gps_data.gps_data_lowpass_filter import GpsDataLowpassFilter


from typing import List
import datetime
import plotly.graph_objects as go


def main():
    sys.argv.append("Drevviken1.gpx")
    sys.argv.append("91")
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("filename", help="File to load datapoints from")
    arg_parser.add_argument("mass", help="Total mass of the bike + rider in kg", type=float)
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
        DragModifyer(cwa=0.6)
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

    avg_power = sum([p.power if p.power>0 else 0 for p in points])/len(points)
    print(f"AVG power: {avg_power}w")


if __name__ == "__main__":
    main()