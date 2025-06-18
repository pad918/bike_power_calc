from .optimizer import Optimizer
from gps_data import GpsDataPoints, GpsDataPoint, GpsDataLowpassFilter
import power_modifyer as pm 
import numpy as np
import random

class SpeedOptimizer(Optimizer):

    def __init__(self, mass, drivetrain_efficency, optimization_steps = 10):
        self._optimization_steps = optimization_steps
        self._mass = mass
        self._drivetrain_efficency = drivetrain_efficency

    def points_from_speeds(self, points:GpsDataPoints, speeds_mps:np.array):
        last_time = points.time[0]
        points_list = points.get_points_list()
        for p0, p1, s in zip(points_list[:-1], points_list[1:], speeds_mps):
            dist_meters = p0.meter_distance_to(p1)
            delta_time = dist_meters/s
            new_time = last_time + np.timedelta64(int(delta_time*1000), "ms")
            last_time = new_time
            p1.time = last_time
            p0.speed = s
        points_list[-1].speed = speeds_mps[-1]
        return GpsDataPoints(points_list)
    
    def score_solution(self, points:GpsDataPoints, target_power):

        # Do not add powers to the original, do it to a clone
        points_clone = points.clone()
        filters = [
            GpsDataLowpassFilter()
        ]

        for filter in filters:
            filter.apply_filter(points=points_clone)

        points_clone.power = np.zeros_like(points.power)

        modifyers = [
            pm.AccelerationModifyer(self._mass),
            pm.ElevationModifyer(self._mass),
            pm.DragModifyer(cwa=0.6, use_weather_data=False),
            pm.RollingForceModifyer(cr=0.007, mass_kg=self._mass),
            pm.DragtrainEfficencyModifyer(efficency=self._drivetrain_efficency)
        ]

        # Apply modifyers
        for modifyer in modifyers:
            modifyer.modify_power_at_points(points_clone)

        power = points_clone.average_power()
        score = max(power - target_power, 0)
        score += points_clone.total_time_hours() * 200
        return score
    
    def create_mutated_speeds(self, speeds:np.array, min_power, max_power):
        speed_clone = speeds.copy()
        l = random.randint(1, min(len(speed_clone), 40))
        start_index = random.randint(0, len(speed_clone)-l-1)

        delta_speed = random.uniform(min_power, max_power)
        for i in range(start_index, start_index+l):
            # Must have at least 1 mps of speed at all points
            speed_clone[i] = max(speed_clone[i]+delta_speed, 1)
        
        return speed_clone

    def optimize_power_curve(self, points, avg_power):
        initial = self.points_from_speeds(points, np.linspace(23/3.6, 23/3.6, len(points.speed)))
        best_score = self.score_solution(initial, avg_power)
        best_solution = initial
        print(f"Score of initial solution: {best_score:.4f}, time: [{best_solution.total_time_hours():.4f}h]")
        for i in range(self._optimization_steps):
            new_speeds = self.create_mutated_speeds(best_solution.speed, -1, 1) # Add some power
            #new_speeds = self.create_mutated_speeds(new_speeds, -3, 0) # Remove some power
            new_solution = self.points_from_speeds(best_solution, new_speeds)
            new_score = self.score_solution(new_solution, target_power=avg_power)
            if(new_score < best_score):
                print(f"Found new best score: {new_score:.4f}, time: [{best_solution.total_time_hours():.4f}h]")
                best_score = new_score
                best_solution = new_solution
            else:
                print(f"\t--- New score: {new_score:.4f}---")

        return best_solution