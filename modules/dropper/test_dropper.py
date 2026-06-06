import time

from modules.dropper.dropper_wrapper import DropperWrapper
from modules.motors import MotorWrapper
from shared_memory import SharedMemoryWrapper

'''
    discord: @alicvo
    github: @alicvo
    
    Simple CLI for testing dropper functionality
'''

port="/dev/ttyUSB0"
BAUDRATE=115200

shared_memory_object = SharedMemoryWrapper()
M = MotorWrapper(shared_memory_object)
dropper = DropperWrapper(shared_memory_object)

if __name__ == "__main__":
    dropper.drop()
    M.send_command()  # send drop command
    time.sleep(2)
    dropper.reset()
    M.send_command()  # send reset command
