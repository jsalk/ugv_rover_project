#!/usr/bin/env python3
# test_motors.py
# Test script for UGV Rover motors

import time
import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from motor_controller import MotorController
    from config import Config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure config.py and motor_controller.py are in the same directory")
    sys.exit(1)

def test_motors():
    """Test all motor functions"""
    print("UGV Rover Motor Test")
    print("=" * 40)
    
    try:
        config = Config()
        motor = MotorController(config)
        
        print("✓ Motor controller initialized")
        print(f"Left motor pins: {config.MOTOR_LEFT_PINS}")
        print(f"Right motor pins: {config.MOTOR_RIGHT_PINS}")
        print(f"Max speed: {config.MAX_SPEED}%")
        print()
        
        # Test sequence
        tests = [
            ("Forward", 50, 50),
            ("Backward", -50, -50),
            ("Turn Right", 50, -50),
            ("Turn Left", -50, 50),
            ("Stop", 0, 0)
        ]
        
        for test_name, left_speed, right_speed in tests:
            print(f"Testing: {test_name}")
            print(f"  Left: {left_speed}, Right: {right_speed}")
            motor.set_speeds(left_speed, right_speed)
            time.sleep(2)
        
        print("\n✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
    finally:
        if 'motor' in locals():
            motor.cleanup()
        print("Motor test finished")

if __name__ == "__main__":
    test_motors()