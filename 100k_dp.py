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
import numpy as np
import time

#   Original : 0.20s or so
#
#
#


def main():
    # Start time measurment
    start = time.time()

    MASS = 100 #kg
    DRIVETRAIN_EFF = 0.95

    # Load gps data
    points = GPXLoader("Drevviken1.gpx").load()
    
    # Apply filters to data
    filters: List[GpsDataFilter] = [
        GpsDataLowpassFilter()
    ]
    for filter in filters:
        filter.apply_filter(points=points)

    modifyers: List[PowerModifyer] = [
        AccelerationModifyer(MASS),
        ElevationModifyer(MASS),
        DragModifyer(cwa=0.6, use_weather_data=False),
        RollingForceModifyer(cr=0.007, mass_kg=MASS),
        DragtrainEfficencyModifyer(efficency=DRIVETRAIN_EFF) # MUST BE LAST
    ]

    # Apply modifyers
    for modifyer in modifyers:
        modifyer.modify_power_at_points(points)

    end = time.time()

    print(f"Total time to run: {end-start}")


if __name__ == "__main__":
    main()

