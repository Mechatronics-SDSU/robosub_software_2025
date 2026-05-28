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
    DROP_COMMAND = b"D" # send as byte
    RESET_COMMAND = b"R"
    
    def __init__(self, port, baudrate, shared_memory_object, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.logger = better_logger.Better_Logger()
        self.shared_memory_object = shared_memory_object

    def _send_command(self, msg, command_name):
        try:
            self.ser.write(msg)
            self.ser.flush()
            self.logger.log_info(f"Dropper: {command_name} command sent successfully.")
        except serial.SerialException as e:
            self.logger.log_error(f"Serial error while sending {command_name} command: {e}")
        except Exception as e:
            self.logger.log_error(f"Error occurred while sending {command_name} command: {e}")

    def drop(self):
        self._send_command(self.DROP_COMMAND, "drop")

    def reset(self):
        self._send_command(self.RESET_COMMAND, "reset")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
