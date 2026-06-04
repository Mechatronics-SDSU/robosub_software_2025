import serial
import modules.logger.better_logger as better_logger
from shared_memory  import SharedMemoryWrapper

'''
    discord: @alicvo
    github: @alicvo
    
    This class is a wrapper for the dropper interface. It is used to send pwm signals to the dropper.
    contains:
        drop method: sends drop pwm to dropper
        reset method: sends reset pwm to dropper

    NOTE: meant for dropper on caracara
'''

class DropperWrapper:
    DROP_PWM = 1500  # PWM value for drop (change if needed)
    RESET_PWM = 300  # PWM value for reset (change if needed i lowkey dont know the values)
    
    def __init__(self, port, baudrate, shared_memory_object, timeout=1):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
        except serial.SerialException as e:
            print(f"DropperWrapper: Error occurred while initializing serial connection: {e}")
        self.logger = better_logger.Better_Logger()
        self.shared_memory_object = shared_memory_object

    def send_pwm(self, pwm, command_name):
        try:
            data = str(pwm).encode()
            self.ser.write(data)
            self.ser.flush()    # wait for the pwm to be sent
            self.logger.log_info(f"DropperWrapper: {command_name} pwm sent successfully.")
        except serial.SerialException as e:
            self.logger.log_error(f"DropperWrapper: Serial error while sending {command_name} pwm: {e}")
        except Exception as e:
            self.logger.log_error(f"DropperWrapper: Error occurred while sending {command_name} pwm: {e}")

    def drop(self, pwm_value=None):
        if pwm_value is not None:
            self.send_pwm(pwm_value, "drop")
        else:
            self.send_pwm(self.DROP_PWM, "drop")

    def reset(self, pwm_value=None):
        if pwm_value is not None:
            self.send_pwm(pwm_value, "reset")
        else:
            self.send_pwm(self.RESET_PWM, "reset")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
