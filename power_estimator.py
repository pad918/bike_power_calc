import argparse
import sys
from gps_data.gpx_loader import GPXLoader
from power_modifyer.power_modifyer import PowerModifyer
from power_modifyer.acceleration_modifyer import AccelerationModifyer
from typing import List
import datetime
import plotly.graph_objects as go


def main():
    sys.argv.append("Drevviken1.gpx")
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("filename", help="File to load datapoints from")
    arg_parser.add_argument("mass", help="Total mass of the bike + rider in kg")
    args = arg_parser.parse_args()

    # Load gps data
    points = GPXLoader(args.filename).load()
    
    modifyers: List[PowerModifyer] = [
        AccelerationModifyer(args.mass)
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


if __name__ == "__main__":
    main()