from .optimizer import Optimizer
from gps_data import GpsDataPoints
import power_modifyer as pm
import numpy as np
import datetime
import math

class IterativeOptimizer(Optimizer):
    
    def __init__(self):
        pass

    def set_speed_and_time_from_power(self, points:GpsDataPoints):
        t = points.time[0]
        speed = 0
        MASS = 90
        EFF = 0.95
        for i in range(1, len(points.power)):
            p0 = points.get_point(i-1)
            p1 = points.get_point(i)
            single = GpsDataPoints([p0, p1])
            modifyers = [
                pm.AccelerationModifyer(MASS),
                pm.ElevationModifyer(MASS),
                pm.DragModifyer(cwa=0.6, use_weather_data=False),
                pm.RollingForceModifyer(cr=0.007, mass_kg=MASS),
                pm.DragtrainEfficencyModifyer(efficency=EFF)
            ]
            for m in modifyers:
                m.modify_power_at_points(single)
            # Calculate current acceleration
            last_speed = max(2, p0.speed)
            force = single.power[0] / last_speed
            acceleration = max(-1, min(force / MASS, 1))
            next_point_dist = max(1, p0.meter_distance_to(p1))

            # Solve polynomial to get time to next point
            a = acceleration
            b = last_speed
            c = -next_point_dist
            if(a<=0 or (b**2-4*a*c)<0):
                # if not possible to calculate, just assume same speed
                time = next_point_dist / last_speed
            else:
                time = -(b/(2*a)) + (b**2-4*a*c)**0.5/(2*a)
            time = max(0.25, min(time, 10))
            speed_at_next_point = max(0, last_speed + time * acceleration) # NO NEGATIVE SPEEDS
            time_stamp = p0.time + datetime.timedelta(seconds=time)
            
            # Update values
            points.time[i] = time_stamp
            points.speed[i] = speed_at_next_point
        

    def get_initial_solution(self, points:GpsDataPoints, avg_power):
        # Use avg power for all points
        points.power = np.full_like(points.power, avg_power)
        self.set_speed_and_time_from_power(points)

    def optimize_power_curve(self, points:GpsDataPoints, avg_power):
        # Return new, optimized points
        optimized_points:GpsDataPoints = points.clone()

        # Set powers and speeds to zero
        optimized_points.power = np.zeros_like(optimized_points.power)
        optimized_points.speed = np.zeros_like(optimized_points.speed)

        # Set times to zero (except first one)
        optimized_points.time[1:] = np.zeros_like(optimized_points.time[1:])

        # Get an initial solution (constant power at all points)
        self.get_initial_solution(optimized_points, avg_power)
        return optimized_points