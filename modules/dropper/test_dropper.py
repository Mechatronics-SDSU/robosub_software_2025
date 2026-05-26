import time

from modules.dropper.dropper_wrapper import DropperWrapper

'''
    discord: @alicvo
    github: @alicvo
    
    Simple CLI for testing dropper functionality
'''

port="/dev/ttyUSB0"
BAUDRATE=115200

if __name__ == "__main__":
    dropper = DropperWrapper(port=port, baudrate=BAUDRATE)
    dropper.drop()
    time.sleep(2)
    dropper.reset()
    dropper.close()
    
