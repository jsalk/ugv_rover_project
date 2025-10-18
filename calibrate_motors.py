#!/usr/bin/env python3
# calibrate_motors.py
# Motor direction calibration script

import time
import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from motor_controller import MotorController
    from config import Config
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def calibrate_motors():
    """Calibrate motor directions"""
    print("UGV Rover Motor Calibration")
    print("=" * 50)
    print("This script helps you calibrate motor directions.")
    print("If motors move in wrong direction, update LEFT_MOTOR_REVERSE")
    print("or RIGHT_MOTOR_REVERSE in config.py")
    print()
    
    try:
        config = Config()
        motor = MotorController(config)
        
        print("Current configuration:")
        print(f"  LEFT_MOTOR_REVERSE: {config.LEFT_MOTOR_REVERSE}")
        print(f"  RIGHT_MOTOR_REVERSE: {config.RIGHT_MOTOR_REVERSE}")
        print()
        
        input("Press Enter to test LEFT motor forward...")
        print("Left motor should move FORWARD")
        motor.set_left_speed(50)
        time.sleep(2)
        motor.stop()
        
        input("Press Enter to test RIGHT motor forward...")
        print("Right motor should move FORWARD")
        motor.set_right_speed(50)
        time.sleep(2)
        motor.stop()
        
        input("Press Enter to test BOTH motors forward...")
        print("Both motors should move FORWARD - rover should go straight ahead")
        motor.set_speeds(50, 50)
        time.sleep(2)
        motor.stop()
        
        print("\nCalibration complete!")
        print("If any motor moved backward instead of forward,")
        print("update the corresponding REVERSE setting in config.py")
        
    except Exception as e:
        print(f"Calibration failed: {e}")
    finally:
        if 'motor' in locals():
            motor.cleanup()

if __name__ == "__main__":
    calibrate_motors()