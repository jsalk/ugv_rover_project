#!/usr/bin/env python3
# examples/simple_drive.py
# Simple autonomous driving example

import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from motor_controller import MotorController
from config import Config

def simple_drive():
    """Simple autonomous driving sequence"""
    print("Simple Autonomous Drive")
    print("=" * 30)
    
    try:
        config = Config()
        motor = MotorController(config)
        
        # Drive forward
        print("Driving forward...")
        motor.set_speeds(50, 50)
        time.sleep(3)
        
        # Turn right
        print("Turning right...")
        motor.set_speeds(50, -50)
        time.sleep(1)
        
        # Drive forward
        print("Driving forward...")
        motor.set_speeds(50, 50)
        time.sleep(2)
        
        # Turn left
        print("Turning left...")
        motor.set_speeds(-50, 50)
        time.sleep(1)
        
        # Stop
        print("Stopping...")
        motor.stop()
        
        print("Drive sequence completed!")
        
    except Exception as e:
        print(f"Drive sequence failed: {e}")
    finally:
        if 'motor' in locals():
            motor.cleanup()

if __name__ == "__main__":
    simple_drive()