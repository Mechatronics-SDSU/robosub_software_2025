import serial

import modules.logger.better_logger as better_logger

'''
    discord: @alicvo
    github: @alicvo
    
    This class is a wrapper for the dropper interface. It is used to send commands to the dropper.
    contains:
        drop method: sends drop command to dropper
        reset method: sends reset command to dropper

    NOTE: meant for dropper on caracara
'''

class DropperWrapper:
    def __init__(self, port, baudrate, timeout=1):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
        self.logger = better_logger.Better_Logger()

    def drop(self):
        try:
            self.serial.write(b'D\n') # send drop command
            self.logger.log_info("Dropper: drop command sent successfully.")
        except Exception as e:
            self.logger.log_error(f"Error occurred while sending drop command: {e}")

    def reset(self):
        try:
            self.serial.write(b'R\n') # send reset command
            self.logger.log_info("Dropper: reset command sent successfully.")
        except Exception as e:
            self.logger.log_error(f"Error occurred while sending reset command: {e}")
    
    def close(self):
        self.serial.close()
