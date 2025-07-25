import serial
# import pyserial
import struct
import numpy

baud_rate = 115200
usb_port = None
srl = None

class USB_Transmitter:
    def __init__(self):
        for port in ["COM3", "/dev/ttyACM0"]:
            try:
                self.srl = serial.Serial(port, baud_rate)
                usb_port = port
                print(f"Connected on {usb_port}")
                break
            except serial.SerialException as e:
                print(f"Failed to connect on {port}: {e}")


    def send_data(self,motor_vals):
        # Check if connection was successful
        if self.srl is None:
            print("❌ Unable to connect to any serial port.")
        else:
            # Proceed with transmitting if serial port is valid
            packed_data = b''
            for num in motor_vals:
                packed_data += struct.pack('<i', num)
            self.srl.write(packed_data)
            print(f"Transmitted: {motor_vals}")
            # # Optional test call
            # usb_transmit([0, 0, 0, 0, 0, 0, 0, 0])
