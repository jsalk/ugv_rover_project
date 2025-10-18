# config.py
# UGV Rover Configuration Settings

import os

class Config:
    """Configuration class for UGV Rover"""
    
    def __init__(self):
        # === Motor Configuration ===
        self.MOTOR_LEFT_PINS = [17, 18]  # GPIO pins for left motor [IN1, IN2]
        self.MOTOR_RIGHT_PINS = [22, 23]  # GPIO pins for right motor [IN1, IN2]
        self.MOTOR_PWM_FREQUENCY = 1000  # PWM frequency in Hz
        self.MOTOR_PWM_RANGE = 100  # PWM range (0-100 for percentage)
        
        # === Motor Driver Type ===
        self.MOTOR_DRIVER_TYPE = "L298N"  # Options: "L298N", "DRV8833", "TB6612FNG"
        
        # === Motor Direction Calibration ===
        self.LEFT_MOTOR_REVERSE = False   # Reverse left motor direction if needed
        self.RIGHT_MOTOR_REVERSE = False  # Reverse right motor direction if needed
        
        # === Speed Limits ===
        self.MAX_SPEED = 80           # Maximum speed percentage (0-100)
        self.MIN_SPEED = 10           # Minimum speed percentage for movement
        self.IDLE_SPEED = 0           # Speed when stopped
        
        # === Controller Configuration ===
        self.XBOX_MAC_ADDRESS = "98:7A:14:AE:3F:0E"
        self.CONTROLLER_DEADZONE = 0.15  # Joystick deadzone (0.0 to 1.0)
        self.CONTROL_RATE = 20        # Control loop frequency in Hz
        
        # === Safety Settings ===
        self.EMERGENCY_STOP_DELAY = 1.0  # Seconds to maintain emergency stop
        self.AUTO_STOP_TIMEOUT = 5.0     # Auto-stop if no controller input (0 to disable)
        
        # === Logging ===
        self.ENABLE_LOGGING = True
        self.LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
        self.LOG_FILE = "ugv_rover.log"
        
        # === Network Settings ===
        self.ENABLE_WEB_INTERFACE = False
        self.WEB_PORT = 8080
        
        # === Camera Settings (if applicable) ===
        self.ENABLE_CAMERA = False
        self.CAMERA_RESOLUTION = (640, 480)
        self.CAMERA_FRAMERATE = 30
        
        # Load environment-specific settings
        self._load_environment_settings()
    
    def _load_environment_settings(self):
        """Load settings from environment variables if present"""
        # Motor settings
        max_speed = os.getenv('UGV_MAX_SPEED')
        if max_speed:
            self.MAX_SPEED = int(max_speed)
        
        mac_address = os.getenv('XBOX_MAC_ADDRESS')
        if mac_address:
            self.XBOX_MAC_ADDRESS = mac_address
        
        # Debug settings
        debug_mode = os.getenv('UGV_DEBUG')
        if debug_mode and debug_mode.lower() == 'true':
            self.LOG_LEVEL = "DEBUG"
    
    def validate(self):
        """Validate configuration settings"""
        if not 0 <= self.MAX_SPEED <= 100:
            raise ValueError("MAX_SPEED must be between 0 and 100")
        
        if not 0 <= self.CONTROLLER_DEADZONE <= 1.0:
            raise ValueError("CONTROLLER_DEADZONE must be between 0.0 and 1.0")
        
        if self.CONTROL_RATE <= 0:
            raise ValueError("CONTROL_RATE must be positive")
        
        return True

# Global config instance
config = Config()