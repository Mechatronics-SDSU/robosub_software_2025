import sys, os, time
from multiprocessing                        import Process, Value
from modules.sensors.trax2.trax_fxns        import TRAX

class Trax_Interface(TRAX):

    """
    discord: @.kech
    github: @rsunderr
    """

    def __init__(self, shared_memory_object) -> None:
        """
        Trax interface constructor
        """
        super().__init__()
        self.shared_memory_object = shared_memory_object
        self.acq_params = (False, False, 0, 0.01) # poll mode false, flush filter false, PNI reserved, 10ms interval
        self.data_components = (6, 0x15, 0x16, 0x17, 0x5, 0x18, 0x19) # 6 comp's: ax ay az yaw pitch roll
        
        # positional values
        self.t_prev = time.time()
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0
        
        # bias compensation
        self.accel_x_bias = 0
        self.accel_y_bias = 0
        self.accel_z_bias = 1
        self.threshold = 0.1

    def run_loop(self) -> None:
        """
        Start the Trax interface process
        """
        self.connect() # connect to trax
        self.send_packet("kStopContinuousMode") # kStopContinuousMode (ensure not running)
        self.send_packet("kSetAcqParams", self.acq_params) # kSetAcqParams - set acquisition parameters
        self.send_packet("kSetDataComponents", self.data_components) # kSetDataComponents - set data components
        self.send_packet("kStartContinuousMode") # kStartContinuousMode - start continuous mode

        while self.shared_memory_object.running.value:
            self.update()

    def update(self) -> None:
        """
        Function targeted by looping multiprocessing calls, called only once
        """
        t = time.time()
        dt = t - self.t_prev
        self.t_prev = t
        try:
            # READ DATA ------------------------------------------------------------------------------------------------------------------------------------------------
            # resp: (byte cout, frame ID, component count, comp ID, value, comp ID, value, ...)
            data = self.recv_packet(self.data_components)
            x_accel   = data[4]
            y_accel   = data[6]
            z_accel   = data[8]
            yaw       = data[10]
            pitch     = data[12]
            roll      = data[14]
            self.shared_memory_object.trax_yaw.value   = yaw
            self.shared_memory_object.trax_pitch.value = pitch
            self.shared_memory_object.trax_roll.value  = roll
            
            # INTEGRATE TO GET VELOCITY AND POSITION ------------------------------------------------------------------------------------------------------------------------------------------------
            dx = x_accel - self.accel_x_bias if abs(x_accel - self.accel_x_bias) > self.threshold else 0
            dy = y_accel - self.accel_y_bias if abs(y_accel - self.accel_y_bias) > self.threshold else 0
            dz = z_accel - self.accel_z_bias if abs(z_accel - self.accel_z_bias) > self.threshold else 0
            self.vel_x += dx * dt
            self.vel_y += dy * dt
            self.vel_z += dz * dt
            self.pos_x += self.vel_x * dt
            self.pos_y += self.vel_y * dt
            self.pos_z += self.vel_z * dt

            print(f"TRAX x: {self.pos_x:.2f}, y: {self.pos_y:.2f}, z: {self.pos_z:.2f}, Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}, X Accel: {x_accel:.2f}, Y Accel: {y_accel:.2f}, Z Accel: {z_accel:.2f}")
        except KeyboardInterrupt:
            # kStopContinuousMode
            self.send_packet("kStopContinuousMode")
            self.close()
        except Exception as e:
            print(f"INVALID TRAX DATA: {e}") # errors are expected