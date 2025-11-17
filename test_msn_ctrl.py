from multiprocessing                        import Process, Value
from shared_memory                          import SharedMemoryWrapper
from fsm.test_fsm                           import Test_FSM
from utils.socket_send                      import set_screen
from modules.test_module.test_process       import Test_Process
from fsm.gate_fsm                               import Gate_FSM
from fsm.slalom_fsm                             import Slalom_FSM
from fsm.octagon_fsm                            import Octagon_FSM
from fsm.return_fsm                             import Return_FSM
import time, os, random, yaml, subprocess


# import modules
# from modules.pid.pid_interface              import PIDInterface
# from modules.sensors.a50_dvl.dvl_interface  import DVL_Interface
# from modules.vision.vision_main             import VisionDetection
# from socket_send                            import set_screen
# from coinflip_fsm                           import CoinFlip_FSM



shared_memory_object = SharedMemoryWrapper()

gate_mode   = Gate_FSM(shared_memory_object, [])
slalom_mode = Slalom_FSM(shared_memory_object, [])
oct_mode    = Octagon_FSM(shared_memory_object, [])
return_mode = Return_FSM(shared_memory_object, [])
mode_list   = [gate_mode, slalom_mode, oct_mode, return_mode]


def move_toward(current_value: float,
                target_value: float,
                test_prop_gain: float = 0.15,
                max_step: float | None = None,
                noise_range: float = 0.05) -> float:
    """
    Move partway toward the target with a small random disturbance.
    - test_prop_gain sets what fraction of the remaining error to move
    - max_step limits how big a single update can be
    - noise_range adds small uniform noise to avoid perfect motion
    """
    error = target_value - current_value
    step_delta = error * test_prop_gain

    """Add a small random disturbance in [-noise_range, +noise_range]."""
    random_disturbance = random.uniform(-noise_range, noise_range)
    step_delta += random_disturbance

    """Limit the step size if a cap is provided."""
    if max_step is not None:
        if step_delta >  max_step: step_delta =  max_step
        if step_delta < -max_step: step_delta = -max_step

    return current_value + step_delta


def approx_equal(current_value: float, target_value: float, absolute_tolerance: float = 0.05) -> bool:
    """
    Return True when current_value is within absolute_tolerance of target_value.
    """
    return abs(current_value - target_value) <= absolute_tolerance
    

def read_yaml_config() -> dict:
    """
    Load YAML into a dict. Return {} on file or parse errors.
    Keeps the loop running even if the file is temporarily invalid.
    """
    try:
        with open(os.path.expanduser("~/robosub_software_2025/objects.yaml"), "r") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        print(f"ERROR: config file not found at {os.path.expanduser('~/robosub_software_2025/objects.yaml')}")
        return {}
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error: {e}")
        return {}


def pick_first_float(d: dict, *keys: str) -> float:
    """
    Return the first present key parsed as float.
    Falls back to 0.0 if none of the keys exist.
    """
    for key in keys:
        if key in d:
            try:
                return float(d[key])
            except (TypeError, ValueError):
                pass
    return 0.0


def read_active_profile_name(config_dict: dict, default_profile_name: str = "test") -> str:
    return str(config_dict.get("course", default_profile_name))


def read_delay_and_multiplier(config_dict: dict, profile_name: str) -> tuple[float, float]:
    profile_block = config_dict.get(profile_name) or {}
    delay_value = float(profile_block.get("delay", 1.0))
    mult_value  = float(profile_block.get("mult", 1.0))
    return delay_value, mult_value


def read_mode_target_xyz_from_config(mode_name: str, config_dict: dict, profile_name: str) -> tuple[float, float, float]:

    profile_block = config_dict.get(profile_name) or {}
    mode_key = str(mode_name or "").lower()

    if mode_key == "gate":
        gate_block = profile_block.get("gate", {}) or {}
        target_x = pick_first_float(gate_block, "x")
        target_y = pick_first_float(gate_block, "y")
        target_z = pick_first_float(gate_block, "z")
        return target_x, target_y, target_z

    if mode_key == "slalom":
        slalom_block = profile_block.get("slalom", {}) or {}
        target_x = pick_first_float(slalom_block, "x1")
        target_y = pick_first_float(slalom_block, "y1")
        target_z = pick_first_float(slalom_block, "z")
        return target_x, target_y, target_z

    if mode_key == "octagon":
        octagon_block = profile_block.get("octagon", {}) or {}
        target_x = pick_first_float(octagon_block, "x")
        target_y = pick_first_float(octagon_block, "y")
        target_z = pick_first_float(octagon_block, "z")
        return target_x, target_y, target_z

    if mode_key == "return":
        return_block = profile_block.get("return", {}) or {}
        target_x = pick_first_float(return_block, "x1")
        target_y = pick_first_float(return_block, "y1")
        target_z = pick_first_float(return_block, "depth")
        return target_x, target_y, target_z

    return 0.0, 0.0, 0.0


def make_list(modes):
    for i in range(len(modes) - 1):
        modes[i].next_mode = modes[i + 1]
    modes[-1].next_mode = None


def display(mode):
    sm = shared_memory_object
    print(f"x: {sm.dvl_x.value:.2f} -> {sm.target_x.value:.2f}")
    print(f"y: {sm.dvl_y.value:.2f} -> {sm.target_y.value:.2f}")
    print(f"z: {sm.dvl_z.value:.2f} -> {sm.target_z.value:.2f}")

    log_entry = {
        "mode": mode.name if mode else "None",
        "state": getattr(mode, "state", "None") if mode else "None",
        "dvl_x": sm.dvl_x.value,
        "dvl_y": sm.dvl_y.value,
        "dvl_z": sm.dvl_z.value,
        "timestamp": time.time(),
    }

    try:
        with open("log.yaml", "r") as file:
            existing_logs = yaml.safe_load(file) or []
    except FileNotFoundError:
        existing_logs = []

    existing_logs.append(log_entry)
    with open("log.yaml", "w") as file:
        yaml.dump(existing_logs, file)

def loop(mode):
    """
    Main control loop.
    - Reloads YAML each iteration so you can live-tune values
    - Updates targets and simulates motion toward them
    - Advances to the next mode once the target is reached
    """
    while shared_memory_object.running.value:
        config_dict = read_yaml_config()
        active_profile_name = read_active_profile_name(config_dict, default_profile_name="test")
        delay_seconds, speed_multiplier = read_delay_and_multiplier(config_dict, active_profile_name)

        target_x, target_y, target_z = read_mode_target_xyz_from_config(
            mode_name=mode.name,
            config_dict=config_dict,
            profile_name=active_profile_name,
        )

        sm = shared_memory_object
        sm.target_x.value = target_x
        sm.target_y.value = target_y
        sm.target_z.value = target_z

        time.sleep(delay_seconds)

        max_step_size = max(1e-6, 0.25 * float(speed_multiplier))
        prop_gain = 0.15

        sm.dvl_x.value = move_toward(sm.dvl_x.value, sm.target_x.value,
                                     test_prop_gain=prop_gain,
                                     max_step=max_step_size,
                                     noise_range=0.05)
        sm.dvl_y.value = move_toward(sm.dvl_y.value, sm.target_y.value,
                                     test_prop_gain=prop_gain,
                                     max_step=max_step_size,
                                     noise_range=0.05)
        sm.dvl_z.value = move_toward(sm.dvl_z.value, sm.target_z.value,
                                     test_prop_gain=prop_gain,
                                     max_step=max_step_size,
                                     noise_range=0.05)
        if hasattr(mode, "complete"):
            mode.complete = (
                approx_equal(sm.dvl_x.value, sm.target_x.value)
                and approx_equal(sm.dvl_y.value, sm.target_y.value)
                and approx_equal(sm.dvl_z.value, sm.target_z.value)
            )

        mode.loop()
        display(mode)

        if getattr(mode, "complete", False):
            next_mode = getattr(mode, "next_mode", None)
            mode = next_mode
            if mode and hasattr(mode, "start"):
                mode.start()
        if mode is None:
            stop()
            break


def stop():
    shared_memory_object.running.value = 0


def main():
    make_list(mode_list)
    starting_mode = mode_list[0]
    starting_mode.start()
    loop(starting_mode)


if __name__ == "__main__":
    print("RUN FROM LAUNCH")
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected, stopping program.")
        shared_memory_object.running.value = 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
