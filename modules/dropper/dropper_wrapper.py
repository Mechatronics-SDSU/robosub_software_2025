import serial
import struct
import modules.logger.better_logger as better_logger
from modules.motors.USB_Transmit    import USB_Transmitter

'''
    discord: @alicvo
    github: @alicvo
    
    This class is a wrapper for the dropper interface. It is used to send pwm signals to the dropper.
    contains:
        drop method: sets current pwm in shared memory to drop value
        reset method: sets current pwm in shared memory to reset value

    NOTE: meant for dropper on caracara
'''

class DropperWrapper:
    DROP_PWM = 1500  # PWM value for drop (change if needed)
    RESET_PWM = 300  # PWM value for reset (change if needed i lowkey dont know the values)
    
    def __init__(self, shared_memory_object):
        self.usb_transmitter = USB_Transmitter()
        self.logger = better_logger.Better_Logger()
        self.shared_memory_object = shared_memory_object

    def drop(self, pwm_value=None):
        if pwm_value is not None:
            pwm = pwm_value
        else:
            pwm = self.DROP_PWM
        self.shared_memory_object.dropper_pwm.value = pwm
        self.logger.log_info(f"DropperWrapper: drop set (PWM: {pwm})")

    def reset(self, pwm_value=None):
        if pwm_value is not None:
            pwm = pwm_value
        else:
            pwm = self.RESET_PWM
        self.shared_memory_object.dropper_pwm.value = pwm
        self.logger.log_info(f"DropperWrapper: reset set (PWM: {pwm})")
