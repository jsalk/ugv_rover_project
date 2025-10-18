#!/usr/bin/env python3
"""
Motor Test Script for Waveshare UGV
Tests all motor movements via GPIO UART connection to ESP32
Uses correct JSON format: {"T":1,"L":0.5,"R":0.5}
"""

import json
import serial
import time
import sys

class UGVMotorTester:
    def __init__(self, serial_port='/dev/serial0', baudrate=115200):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.ser = None
        self.running = True
        
    def connect(self):
        """Initialize serial connection to ESP32 via GPIO UART"""
        try:
            self.ser = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            # Clear any pending data
            if self.ser.in_waiting:
                self.ser.reset_input_buffer()
                
            time.sleep(2)  # Wait for connection to establish
            print(f"Connected to ESP32 via {self.serial_port} at {self.baudrate} baud")
            return True
        except Exception as e:
            print(f"Error connecting to {self.serial_port}: {e}")
            print("Please ensure:")
            print("1. Serial is enabled in raspi-config")
            print("2. ESP32 is properly connected to Raspberry Pi GPIO")
            print("3. No other services are using the serial port")
            return False

    def send_motor_command(self, left_speed, right_speed):
        """Send motor command in correct JSON format: {"T":1,"L":0.5,"R":0.5}"""
        cmd = {
            "T": 1,  # Motor command type
            "L": left_speed,  # Left motor speed (-1.0 to 1.0)
            "R": right_speed   # Right motor speed (-1.0 to 1.0)
        }
        
        try:
            json_cmd = json.dumps(cmd) + '\n'
            self.ser.write(json_cmd.encode())
            self.ser.flush()  # Ensure data is sent
            print(f"Sent: {cmd}")
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False

    def stop_motors(self):
        """Stop both motors"""
        self.send_motor_command(0.0, 0.0)
        print("Motors stopped")

    def test_forward(self, speed=0.5, duration=2):
        """Test forward movement"""
        print(f"Moving forward at speed {speed} for {duration} seconds...")
        self.send_motor_command(speed, speed)
        time.sleep(duration)
        self.stop_motors()

    def test_backward(self, speed=0.5, duration=2):
        """Test backward movement"""
        print(f"Moving backward at speed {speed} for {duration} seconds...")
        self.send_motor_command(-speed, -speed)
        time.sleep(duration)
        self.stop_motors()

    def test_turn_left(self, speed=0.5, duration=2):
        """Test left turn (point turn)"""
        print(f"Turning left at speed {speed} for {duration} seconds...")
        self.send_motor_command(-speed, speed)  # Left backward, right forward
        time.sleep(duration)
        self.stop_motors()

    def test_turn_right(self, speed=0.5, duration=2):
        """Test right turn (point turn)"""
        print(f"Turning right at speed {speed} for {duration} seconds...")
        self.send_motor_command(speed, -speed)  # Left forward, right backward
        time.sleep(duration)
        self.stop_motors()

    def test_pivot_left(self, speed=0.5, duration=2):
        """Test pivot left (one wheel stationary)"""
        print(f"Pivoting left at speed {speed} for {duration} seconds...")
        self.send_motor_command(0.0, speed)  # Left stop, right forward
        time.sleep(duration)
        self.stop_motors()

    def test_pivot_right(self, speed=0.5, duration=2):
        """Test pivot right (one wheel stationary)"""
        print(f"Pivoting right at speed {speed} for {duration} seconds...")
        self.send_motor_command(speed, 0.0)  # Left forward, right stop
        time.sleep(duration)
        self.stop_motors()

    def test_curve_left(self, speed=0.5, duration=2):
        """Test curve left (both forward, left slower)"""
        print(f"Curving left at speed {speed} for {duration} seconds...")
        self.send_motor_command(speed * 0.3, speed)  # Left slower, right normal
        time.sleep(duration)
        self.stop_motors()

    def test_curve_right(self, speed=0.5, duration=2):
        """Test curve right (both forward, right slower)"""
        print(f"Curving right at speed {speed} for {duration} seconds...")
        self.send_motor_command(speed, speed * 0.3)  # Left normal, right slower
        time.sleep(duration)
        self.stop_motors()

    def test_differential_speeds(self):
        """Test different speed combinations"""
        print("Testing differential speeds...")
        
        speed_combinations = [
            (0.3, 0.5, "Gentle left curve"),
            (0.5, 0.3, "Gentle right curve"),
            (-0.3, -0.5, "Backward gentle left"),
            (-0.5, -0.3, "Backward gentle right"),
            (0.8, 0.2, "Sharp right curve"),
            (0.2, 0.8, "Sharp left curve"),
        ]
        
        for left_speed, right_speed, description in speed_combinations:
            print(f"{description} - L:{left_speed}, R:{right_speed}")
            self.send_motor_command(left_speed, right_speed)
            time.sleep(2)
            self.stop_motors()
            time.sleep(0.5)

    def test_speed_ramp(self):
        """Test speed ramp from slow to fast"""
        print("Testing forward speed ramp...")
        speeds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        
        for speed in speeds:
            print(f"Speed: {speed:.1f}")
            self.send_motor_command(speed, speed)
            time.sleep(0.5)
        
        self.stop_motors()
        
        print("Testing backward speed ramp...")
        speeds = [-0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9, -1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1]
        
        for speed in speeds:
            print(f"Speed: {speed:.1f}")
            self.send_motor_command(speed, speed)
            time.sleep(0.5)
        
        self.stop_motors()

    def run_automated_test(self):
        """Run a complete automated test sequence"""
        tests = [
            ("Forward", lambda: self.test_forward(speed=0.3, duration=1.5)),
            ("Backward", lambda: self.test_backward(speed=0.3, duration=1.5)),
            ("Turn Left", lambda: self.test_turn_left(speed=0.4, duration=1.5)),
            ("Turn Right", lambda: self.test_turn_right(speed=0.4, duration=1.5)),
            ("Pivot Left", lambda: self.test_pivot_left(speed=0.4, duration=1.5)),
            ("Pivot Right", lambda: self.test_pivot_right(speed=0.4, duration=1.5)),
            ("Curve Left", lambda: self.test_curve_left(speed=0.4, duration=1.5)),
            ("Curve Right", lambda: self.test_curve_right(speed=0.4, duration=1.5)),
            ("Differential Speeds", self.test_differential_speeds),
            ("Speed Ramp", self.test_speed_ramp)
        ]
        
        print("Starting automated motor test sequence...")
        print("="*60)
        print("IMPORTANT: Elevate the UGV so wheels can spin freely!")
        print("Speed range: -1.0 (full backward) to 1.0 (full forward)")
        print("="*60)
        input("Press Enter to start or Ctrl+C to cancel...")
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"Running: {test_name}")
            print(f"{'='*50}")
            
            try:
                test_func()
                time.sleep(1)  # Pause between tests
            except KeyboardInterrupt:
                print("\nTest interrupted by user")
                self.stop_motors()
                break
            except Exception as e:
                print(f"Error during {test_name}: {e}")
                self.stop_motors()

    def manual_control(self):
        """Manual control mode"""
        print("\nManual Control Mode")
        print("Commands: w=forward, s=backward, a=left, d=right, q=stop, x=exit")
        print("Speed control: 1=slow, 2=medium, 3=fast, 4=very fast")
        print("Special: z=pivot left, c=pivot right, e=curve left, r=curve right")
        
        speed_levels = {
            '1': 0.2,  # Slow
            '2': 0.5,  # Medium
            '3': 0.8,  # Fast
            '4': 1.0   # Very fast
        }
        current_speed = 0.5
        
        while self.running:
            try:
                key = input("Enter command: ").lower().strip()
                
                if key == 'w':
                    self.send_motor_command(current_speed, current_speed)
                    print(f"Moving forward at speed {current_speed}")
                elif key == 's':
                    self.send_motor_command(-current_speed, -current_speed)
                    print(f"Moving backward at speed {current_speed}")
                elif key == 'a':
                    self.send_motor_command(-current_speed, current_speed)
                    print(f"Turning left at speed {current_speed}")
                elif key == 'd':
                    self.send_motor_command(current_speed, -current_speed)
                    print(f"Turning right at speed {current_speed}")
                elif key == 'z':
                    self.send_motor_command(0.0, current_speed)
                    print(f"Pivoting left at speed {current_speed}")
                elif key == 'c':
                    self.send_motor_command(current_speed, 0.0)
                    print(f"Pivoting right at speed {current_speed}")
                elif key == 'e':
                    self.send_motor_command(current_speed * 0.3, current_speed)
                    print(f"Curving left at speed {current_speed}")
                elif key == 'r':
                    self.send_motor_command(current_speed, current_speed * 0.3)
                    print(f"Curving right at speed {current_speed}")
                elif key == 'q':
                    self.stop_motors()
                    print("Stopped")
                elif key in speed_levels:
                    current_speed = speed_levels[key]
                    print(f"Speed set to {current_speed}")
                elif key == 'x':
                    self.stop_motors()
                    print("Exiting manual control")
                    break
                else:
                    print("Invalid command")
                    
            except KeyboardInterrupt:
                self.stop_motors()
                print("\nExiting manual control")
                break

    def test_individual_movement(self):
        """Test individual movement patterns"""
        print("\nIndividual Movement Tests:")
        print("1. Forward")
        print("2. Backward") 
        print("3. Turn Left (Point Turn)")
        print("4. Turn Right (Point Turn)")
        print("5. Pivot Left")
        print("6. Pivot Right")
        print("7. Curve Left")
        print("8. Curve Right")
        print("9. Custom Speed Test")
        
        try:
            test_choice = input("Select test (1-9): ").strip()
            
            if test_choice in ['1', '2']:
                duration = float(input("Duration (seconds, default 2): ") or "2")
                speed = float(input("Speed (0.1-1.0, default 0.5): ") or "0.5")
                
                if test_choice == '1':
                    self.test_forward(speed, duration)
                else:
                    self.test_backward(speed, duration)
                    
            elif test_choice in ['3', '4', '5', '6', '7', '8']:
                duration = float(input("Duration (seconds, default 2): ") or "2")
                speed = float(input("Speed (0.1-1.0, default 0.5): ") or "0.5")
                
                tests = {
                    '3': self.test_turn_left,
                    '4': self.test_turn_right,
                    '5': self.test_pivot_left,
                    '6': self.test_pivot_right,
                    '7': self.test_curve_left,
                    '8': self.test_curve_right
                }
                tests[test_choice](speed, duration)
                
            elif test_choice == '9':
                left_speed = float(input("Left motor speed (-1.0 to 1.0): "))
                right_speed = float(input("Right motor speed (-1.0 to 1.0): "))
                duration = float(input("Duration (seconds): "))
                
                print(f"Testing custom speeds - L:{left_speed}, R:{right_speed} for {duration}s")
                self.send_motor_command(left_speed, right_speed)
                time.sleep(duration)
                self.stop_motors()
                
            else:
                print("Invalid choice")
                
        except ValueError:
            print("Invalid input. Please enter numbers.")
        except KeyboardInterrupt:
            self.stop_motors()
            print("\nTest cancelled")

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.ser and self.ser.is_open:
            self.stop_motors()
            self.ser.close()
            print("Serial connection closed")

def check_serial_config():
    """Check if serial is properly configured"""
    print("Checking serial configuration...")
    
    # Check if serial is enabled
    try:
        with open('/boot/config.txt', 'r') as f:
            config_content = f.read()
            if 'enable_uart=1' not in config_content:
                print("⚠️  Warning: enable_uart=1 not found in /boot/config.txt")
            else:
                print("✓ Serial UART enabled in config.txt")
    except:
        print("⚠️  Could not check /boot/config.txt")
    
    print("\nGPIO UART Pinout:")
    print("Raspberry Pi TX (GPIO 14) -> ESP32 RX")
    print("Raspberry Pi RX (GPIO 15) -> ESP32 TX")
    print("GND -> GND")
    
    print("\nCommand Format: {'T': 1, 'L': -1.0 to 1.0, 'R': -1.0 to 1.0}")

def main():
    print("Waveshare UGV Motor Test - GPIO UART Version")
    print("Using command format: {'T': 1, 'L': 0.5, 'R': 0.5}")
    print("="*50)
    
    # Check serial configuration
    check_serial_config()
    print()
    
    # Try GPIO serial ports
    possible_ports = ['/dev/serial0', '/dev/ttyAMA0', '/dev/ttyS0']
    tester = None
    
    for port in possible_ports:
        print(f"Trying to connect to {port}...")
        tester = UGVMotorTester(serial_port=port)
        if tester.connect():
            break
        tester = None
    
    if not tester:
        print("❌ Could not connect to ESP32 via GPIO UART")
        print("Please check:")
        print("1. Physical connections (TX->RX, RX->TX, GND->GND)")
        print("2. Serial is enabled: sudo raspi-config -> Interface Options -> Serial")
        print("3. ESP32 is powered on and programmed")
        return
    
    try:
        while True:
            print("\n" + "="*50)
            print("Waveshare UGV Motor Test Menu")
            print("="*50)
            print("1. Run Automated Test Sequence")
            print("2. Manual Control")
            print("3. Test Individual Movement")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                tester.run_automated_test()
            elif choice == '2':
                tester.manual_control()
            elif choice == '3':
                tester.test_individual_movement()
            elif choice == '4':
                break
            else:
                print("Invalid choice")
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        tester.cleanup()
        print("Test completed")

if __name__ == "__main__":
    main()