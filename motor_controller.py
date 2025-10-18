# motor_controller.py
# Motor Controller for UGV Rover using L298N or similar drivers

import time
import logging
import RPi.GPIO as GPIO

class MotorController:
    """Motor controller for UGV Rover using L298N driver"""
    
    def __init__(self, config=None):
        from config import Config
        self.config = config or Config()
        self.logger = self._setup_logging()
        
        # Motor state
        self.left_speed = 0
        self.right_speed = 0
        self.is_initialized = False
        
        # Initialize GPIO and motors
        self._init_gpio()
        self._init_motors()
        
        self.logger.info("MotorController initialized")
    
    def _setup_logging(self):
        """Setup logging for motor controller"""
        logger = logging.getLogger('MotorController')
        if self.config.ENABLE_LOGGING:
            level = getattr(logging, self.config.LOG_LEVEL.upper(), logging.INFO)
            logger.setLevel(level)
            
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
        
        return logger
    
    def _init_gpio(self):
        """Initialize GPIO settings"""
        try:
            GPIO.setmode(GPIO.BCM)  # Use BCM numbering
            GPIO.setwarnings(False)
            
            # Setup motor pins
            all_pins = self.config.MOTOR_LEFT_PINS + self.config.MOTOR_RIGHT_PINS
            for pin in all_pins:
                GPIO.setup(pin, GPIO.OUT)
            
            self.is_initialized = True
            self.logger.info("GPIO initialized successfully")
            
        except Exception as e:
            self.logger.error(f"GPIO initialization failed: {e}")
            raise
    
    def _init_motors(self):
        """Initialize motors to stopped state"""
        self.stop()
        self.logger.info("Motors initialized in stopped state")
    
    def set_left_speed(self, speed):
        """Set left motor speed (-100 to 100)"""
        if not self.is_initialized:
            self.logger.warning("Motor controller not initialized")
            return
        
        # Validate and clamp speed
        speed = max(-100, min(100, speed))
        self.left_speed = speed
        
        # Apply direction reversal if configured
        if self.config.LEFT_MOTOR_REVERSE:
            speed = -speed
        
        # Convert to actual motor commands
        self._set_motor_speed(self.config.MOTOR_LEFT_PINS, speed, "left")
        
        self.logger.debug(f"Left motor speed set to: {speed}")
    
    def set_right_speed(self, speed):
        """Set right motor speed (-100 to 100)"""
        if not self.is_initialized:
            self.logger.warning("Motor controller not initialized")
            return
        
        # Validate and clamp speed
        speed = max(-100, min(100, speed))
        self.right_speed = speed
        
        # Apply direction reversal if configured
        if self.config.RIGHT_MOTOR_REVERSE:
            speed = -speed
        
        # Convert to actual motor commands
        self._set_motor_speed(self.config.MOTOR_RIGHT_PINS, speed, "right")
        
        self.logger.debug(f"Right motor speed set to: {speed}")
    
    def _set_motor_speed(self, pins, speed, motor_name):
        """Set motor speed using L298N control logic"""
        in1, in2 = pins
        
        if speed > 0:
            # Forward
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
        elif speed < 0:
            # Backward
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
        else:
            # Stop
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
    
    def set_speeds(self, left_speed, right_speed):
        """Set both motor speeds at once"""
        self.set_left_speed(left_speed)
        self.set_right_speed(right_speed)
    
    def stop(self):
        """Stop both motors immediately"""
        self.left_speed = 0
        self.right_speed = 0
        
        # Stop left motor
        in1, in2 = self.config.MOTOR_LEFT_PINS
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        
        # Stop right motor
        in1, in2 = self.config.MOTOR_RIGHT_PINS
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        
        self.logger.info("All motors stopped")
    
    def get_speeds(self):
        """Get current motor speeds"""
        return {
            'left': self.left_speed,
            'right': self.right_speed
        }
    
    def emergency_stop(self):
        """Emergency stop - alias for stop()"""
        self.logger.warning("EMERGENCY STOP ACTIVATED")
        self.stop()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            self.stop()
            GPIO.cleanup()
            self.is_initialized = False
            self.logger.info("MotorController cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

# Factory function to create appropriate motor controller
def create_motor_controller(config=None):
    """Factory function to create the appropriate motor controller"""
    from config import Config
    config = config or Config()
    
    return MotorController(config)