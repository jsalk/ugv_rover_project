#!/usr/bin/env python3
# examples/autonomous_template.py
# Template for autonomous navigation

import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from motor_controller import MotorController
from config import Config

class AutonomousRover:
    def __init__(self):
        self.config = Config()
        self.motor = MotorController(self.config)
        self.running = False
    
    def avoid_obstacle(self):
        """Simple obstacle avoidance behavior"""
        print("Obstacle detected! Avoiding...")
        
        # Back up slightly
        self.motor.set_speeds(-30, -30)
        time.sleep(1)
        
        # Turn right
        self.motor.set_speeds(40, -40)
        time.sleep(1.5)
        
        # Continue forward
        self.motor.set_speeds(50, 50)
    
    def follow_line(self, sensor_readings):
        """Basic line following algorithm"""
        left_sensor, right_sensor = sensor_readings
        
        if left_sensor and right_sensor:
            # Both sensors on line - go straight
            self.motor.set_speeds(40, 40)
        elif left_sensor and not right_sensor:
            # Only left on line - turn left
            self.motor.set_speeds(20, 40)
        elif not left_sensor and right_sensor:
            # Only right on line - turn right
            self.motor.set_speeds(40, 20)
        else:
            # No line detected - search
            self.motor.set_speeds(30, -30)
    
    def run_autonomous(self, duration=30):
        """Run autonomous navigation for specified duration"""
        print(f"Starting autonomous navigation for {duration} seconds...")
        self.running = True
        start_time = time.time()
        
        try:
            while self.running and (time.time() - start_time) < duration:
                # Main autonomous loop
                # Add your sensor readings and logic here
                
                # Example: Simple forward movement with periodic turns
                current_time = time.time() - start_time
                
                if current_time < 10:
                    # First 10 seconds: drive forward
                    self.motor.set_speeds(50, 50)
                elif current_time < 15:
                    # Next 5 seconds: turn right
                    self.motor.set_speeds(50, -50)
                elif current_time < 25:
                    # Next 10 seconds: drive forward
                    self.motor.set_speeds(50, 50)
                else:
                    # Last 5 seconds: turn left
                    self.motor.set_speeds(-50, 50)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("Autonomous navigation interrupted")
        finally:
            self.stop()
    
    def stop(self):
        """Stop autonomous navigation"""
        self.running = False
        self.motor.stop()
        print("Autonomous navigation stopped")

if __name__ == "__main__":
    rover = AutonomousRover()
    
    try:
        rover.run_autonomous(30)
    except Exception as e:
        print(f"Autonomous operation failed: {e}")
    finally:
        rover.stop()