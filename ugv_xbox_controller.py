#!/usr/bin/env python3
# ugv_xbox_controller.py

import pygame
import time
import subprocess
import os
import sys

# Add the UGV project path to import motor controllers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from motor_controller import MotorController
    from config import Config
    UGV_AVAILABLE = True
except ImportError:
    print("Warning: UGV project modules not found. Running in test mode.")
    UGV_AVAILABLE = False

class UGVXboxController:
    def __init__(self):
        self.joystick = None
        self.motor_controller = None
        self.config = None
        
        # Initialize UGV project components
        self.init_ugv_components()
        
        # Controller settings
        self.deadzone = getattr(self.config, 'CONTROLLER_DEADZONE', 0.15)
        self.max_speed = getattr(self.config, 'MAX_SPEED', 80)
        self.control_rate = getattr(self.config, 'CONTROL_RATE', 20)
        self.mac_address = getattr(self.config, 'XBOX_MAC_ADDRESS', "98:7A:14:AE:3F:0E")
        
        # Xbox Controller Mapping
        self.AXIS_LEFT_X = 0
        self.AXIS_LEFT_Y = 1
        self.AXIS_RIGHT_X = 2
        self.AXIS_RIGHT_Y = 3
        self.AXIS_LEFT_TRIGGER = 4
        self.AXIS_RIGHT_TRIGGER = 5
        
        self.BUTTON_A = 0
        self.BUTTON_B = 1
        self.BUTTON_X = 2
        self.BUTTON_Y = 3
        self.BUTTON_LB = 4
        self.BUTTON_RB = 5
        self.BUTTON_BACK = 6
        self.BUTTON_START = 7
        self.BUTTON_XBOX = 8
        
        self.init_controller()
        
    def init_ugv_components(self):
        """Initialize UGV project motor controller and config"""
        if UGV_AVAILABLE:
            try:
                self.config = Config()
                self.motor_controller = MotorController(self.config)
                print("✓ UGV motor controller initialized")
            except Exception as e:
                print(f"⚠ UGV component initialization warning: {e}")
                self.motor_controller = None
                self.config = type('Config', (), {})()
        else:
            print("⚠ Running in test mode - no motor control")
            self.motor_controller = None
            self.config = type('Config', (), {})()

    def ensure_connection(self):
        """Make sure controller is connected"""
        try:
            result = subprocess.run(['bluetoothctl', 'info', self.mac_address], 
                                  capture_output=True, text=True)
            if 'Connected: yes' not in result.stdout:
                print("Controller not connected, attempting to connect...")
                subprocess.run(['bluetoothctl', 'connect', self.mac_address], 
                             capture_output=True)
                time.sleep(3)
        except Exception as e:
            print(f"Connection check error: {e}")

    def init_controller(self):
        """Initialize the Xbox controller"""
        print("Initializing Xbox controller for UGV...")
        self.ensure_connection()
        
        pygame.init()
        pygame.joystick.init()
        
        max_attempts = 10
        for attempt in range(max_attempts):
            joystick_count = pygame.joystick.get_count()
            if joystick_count > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"✓ Xbox controller connected: {self.joystick.get_name()}")
                return
            else:
                print(f"Waiting for controller... ({attempt + 1}/{max_attempts})")
                time.sleep(1)
        
        print("✗ Could not detect controller after 10 seconds")
        exit()

    def apply_deadzone(self, value):
        """Apply deadzone to joystick values"""
        if abs(value) < self.deadzone:
            return 0.0
        return value

    def map_speed(self, value):
        """Map joystick value to motor speed"""
        return int(self.apply_deadzone(value) * self.max_speed)

    def mix_controls(self, throttle, steering):
        """Differential drive mixing for UGV chassis"""
        left_speed = throttle + steering
        right_speed = throttle - steering
        
        max_val = max(abs(left_speed), abs(right_speed))
        if max_val > self.max_speed:
            scale = self.max_speed / max_val
            left_speed *= scale
            right_speed *= scale
            
        return int(left_speed), int(right_speed)

    def get_controls_left_stick(self):
        """Control Scheme 1: Left stick for both throttle and steering"""
        throttle = -self.joystick.get_axis(self.AXIS_LEFT_Y)
        steering = self.joystick.get_axis(self.AXIS_LEFT_X)
        return throttle, steering

    def get_controls_trigger_stick(self):
        """Control Scheme 2: Triggers for throttle, right stick for steering"""
        forward = self.joystick.get_axis(self.AXIS_RIGHT_TRIGGER)
        backward = self.joystick.get_axis(self.AXIS_LEFT_TRIGGER)
        throttle = forward - backward
        steering = self.joystick.get_axis(self.AXIS_RIGHT_X)
        return throttle, steering

    def get_controls_dual_stick(self):
        """Control Scheme 3: Left stick for throttle, right stick for steering"""
        throttle = -self.joystick.get_axis(self.AXIS_LEFT_Y)
        steering = self.joystick.get_axis(self.AXIS_RIGHT_X)
        return throttle, steering

    def set_motor_speeds(self, left_speed, right_speed):
        """Set motor speeds using UGV motor controller"""
        if self.motor_controller:
            try:
                self.motor_controller.set_left_speed(left_speed)
                self.motor_controller.set_right_speed(right_speed)
            except Exception as e:
                print(f"Motor control error: {e}")
        else:
            print(f"[MOTORS] L: {left_speed:3d}, R: {right_speed:3d}")

    def stop_motors(self):
        """Stop all motors"""
        if self.motor_controller:
            try:
                self.motor_controller.stop()
            except Exception as e:
                print(f"Motor stop error: {e}")
        else:
            print("[MOTORS] STOPPED")

    def run(self):
        """Main control loop"""
        control_scheme = 1
        last_scheme_change = time.time()
        scheme_change_delay = 0.5
        
        print("\n" + "=" * 50)
        print("UGV Rover - Xbox Controller")
        print("=" * 50)
        print("Control Schemes:")
        print("  X Button: Left Stick (Throttle + Steering)")
        print("  Y Button: Triggers (Throttle) + Right Stick (Steering)")
        print("  B Button: Dual Stick (Left: Throttle, Right: Steering)")
        print("\nControls:")
        print("  A Button: Emergency Stop")
        print("  Back Button: Exit Program")
        print("  Start Button: Toggle motor enable")
        print("  LB/RB: Adjust max speed")
        print("=" * 50)
        
        motor_enabled = True
        last_motor_toggle = time.time()
        
        try:
            while True:
                pygame.event.pump()
                current_time = time.time()
                
                # Switch control schemes
                if (current_time - last_scheme_change > scheme_change_delay):
                    if self.joystick.get_button(self.BUTTON_X):
                        control_scheme = 1
                        print("Control Scheme 1: Left Stick")
                        last_scheme_change = current_time
                    elif self.joystick.get_button(self.BUTTON_Y):
                        control_scheme = 2  
                        print("Control Scheme 2: Triggers + Right Stick")
                        last_scheme_change = current_time
                    elif self.joystick.get_button(self.BUTTON_B):
                        control_scheme = 3
                        print("Control Scheme 3: Dual Stick")
                        last_scheme_change = current_time
                
                # Adjust max speed
                if self.joystick.get_button(self.BUTTON_LB):
                    self.max_speed = max(10, self.max_speed - 10)
                    print(f"Max speed decreased to: {self.max_speed}")
                    time.sleep(0.3)
                elif self.joystick.get_button(self.BUTTON_RB):
                    self.max_speed = min(100, self.max_speed + 10)
                    print(f"Max speed increased to: {self.max_speed}")
                    time.sleep(0.3)
                
                # Toggle motor enable
                if (current_time - last_motor_toggle > scheme_change_delay and 
                    self.joystick.get_button(self.BUTTON_START)):
                    motor_enabled = not motor_enabled
                    status = "ENABLED" if motor_enabled else "DISABLED"
                    print(f"Motors {status}")
                    last_motor_toggle = current_time
                    if not motor_enabled:
                        self.stop_motors()
                
                # Get controls
                if control_scheme == 1:
                    throttle, steering = self.get_controls_left_stick()
                elif control_scheme == 2:
                    throttle, steering = self.get_controls_trigger_stick()
                else:
                    throttle, steering = self.get_controls_dual_stick()
                
                # Calculate motor speeds
                left_speed, right_speed = self.mix_controls(
                    self.map_speed(throttle), 
                    self.map_speed(steering)
                )
                
                # Control motors
                if motor_enabled:
                    self.set_motor_speeds(left_speed, right_speed)
                
                # Display status
                scheme_names = {1: "L-Stick", 2: "Triggers", 3: "Dual-Stick"}
                motor_status = "ON" if motor_enabled else "OFF"
                print(f"[{scheme_names[control_scheme]}] Throttle: {throttle:6.2f}, Steering: {steering:6.2f} -> L: {left_speed:3d}, R: {right_speed:3d} | Motors: {motor_status} | Max: {self.max_speed}%", end='\r')
                
                # Emergency stop
                if self.joystick.get_button(self.BUTTON_A):
                    print("\n*** EMERGENCY STOP! ***")
                    self.stop_motors()
                    motor_enabled = False
                    time.sleep(1)
                
                # Exit
                if self.joystick.get_button(self.BUTTON_BACK):
                    print("\nBack button pressed. Exiting...")
                    break
                    
                time.sleep(1.0 / self.control_rate)
                
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up UGV controller...")
        self.stop_motors()
        if self.motor_controller:
            self.motor_controller.cleanup()
        pygame.quit()
        print("UGV controller shutdown complete.")

def main():
    """Main function for UGV project integration"""
    print("Starting UGV Xbox Controller...")
    
    try:
        controller = UGVXboxController()
        controller.run()
    except Exception as e:
        print(f"Failed to start UGV controller: {e}")
        pygame.quit()

if __name__ == "__main__":
    main()