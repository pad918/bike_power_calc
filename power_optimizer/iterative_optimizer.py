from .optimizer import Optimizer
from gps_data import GpsDataPoints, GpsDataPoint
import power_modifyer as pm
import numpy as np
import datetime
import math
import random

class IterativeOptimizer(Optimizer):
    
    def __init__(self):
        pass

    def set_speed_and_time_from_power(self, points:GpsDataPoints):
        points.speed = np.zeros_like(points.speed)
        points.time[1:] = np.zeros_like(points.time[1:])
        t = points.time[0]
        speed = 0
        MASS = 90
        EFF = 0.95
        for i in range(1, len(points.power)):
            p0 = points.get_point(i-1)
            p1 = points.get_point(i)
            single = GpsDataPoints([p0, p1])
            single.power = np.zeros_like(single.power)
            modifyers = [
                #pm.AccelerationModifyer(MASS),
                pm.ElevationModifyer(MASS),
                pm.DragModifyer(cwa=0.6, use_weather_data=False),
                pm.RollingForceModifyer(cr=0.007, mass_kg=MASS),
                pm.DragtrainEfficencyModifyer(efficency=EFF)
            ]
            for m in modifyers:
                m.modify_power_at_points(single)
            single.power *= -1
            total_power = single.power[0] + p0.power

            # Calculate current acceleration
            last_speed = max(2, p0.speed)
            force = total_power / last_speed
            acceleration = max(-3, min(force / MASS, 3))
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
        

    def score_solution(self, points:GpsDataPoints, target_power):
        MASS = 90
        EFF = 0.95
        points.power = np.zeros_like(points.power)
        modifyers = [
            pm.AccelerationModifyer(MASS),
            pm.ElevationModifyer(MASS),
            pm.DragModifyer(cwa=0.6, use_weather_data=False),
            pm.RollingForceModifyer(cr=0.007, mass_kg=MASS),
            pm.DragtrainEfficencyModifyer(efficency=EFF)
        ]

        # Apply modifyers
        for modifyer in modifyers:
            modifyer.modify_power_at_points(points)
        avg_power = points.average_power()
        score = max(0, avg_power - target_power)
        score += points.total_time_hours() * 5
        return score

    def get_initial_solution(self, points:GpsDataPoints, avg_power):
        # Use avg power for all points
        points.power = np.loadtxt("saved.gz") #np.full_like(points.power, avg_power)
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
        original_time = optimized_points.total_time_hours()
        print(f"ORIGINAL TIME: {original_time:.4f}h")
        best_powers = optimized_points.power.copy()
        def update(points:GpsDataPoints, powers):
            points.power = powers.copy()
            self.set_speed_and_time_from_power(points)
            print(f"UPDATED TOTAL TIME: {points.total_time_hours():.4f}h : i: {i}")

        init_score = self.score_solution(optimized_points, avg_power)
        print(f"Initial score: {init_score:.4f}")
        best_score = init_score
        for i in range(int(200)):
            if (i%1000==0):
                print(f"Saving at {i}")
                np.savetxt(f"save_{i}.gz", best_powers)

            # Optimize solution
            powers_to_test = best_powers.copy()
            # Update powers in some way
            for _ in range(1):
                j = random.randint(0, len(points.power)-100-1)
                delta = random.randrange(-40, 40, 1)
                m = 100
                if(i>200):
                    m = 20
                if(i>400):
                    m = 5
                l = random.randint(3, m)
                for o in range(j, j+l):
                    powers_to_test[o] += delta

            # Test new powers
            update(optimized_points, powers_to_test)
            new_score = self.score_solution(optimized_points, avg_power)
            
            if(new_score<best_score):
                best_time = optimized_points.total_time_hours()
                print(f"Found new best score: {new_score:.4f}, {original_time:.4f}h --> {best_time:.4f}h, [{((best_time/original_time-1)*100):.4f}%]")
                best_score = new_score
                best_powers = powers_to_test
        
        # Apply the best powers and return
        update(optimized_points, best_powers)
        update(optimized_points, best_powers)
        np.savetxt("solution_power_vector.gz", best_powers)
        return optimized_points