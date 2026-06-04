# Dropper Wrapper Interface

Software wrapper for CaraCara's dropper mechanism. Provides a high-level interface 
for controlling the dropper system during a run.

### Outline

- Date Created: 05/25/2026
- Contributors:
    - Alice Vo (GitHub: @alicvo, Discord: @alicvo)
- Dependencies:
    - Python 3.11+
    - Pyserial 3.5

### Key Files

- dropper_wrapper.py
    - Main wrapper interface for controlling the dropper mechanism
- test_dropper.py
    - Test script for validating dropper operation

### Usage

- Run `python test_dropper.py` to validate functionality

The dropper firmware receives PWM values (in microseconds) sent to the STM32:
**Commands:**
- `drop()`
  - Without argument: uses `DROP_PWM = 1500` (predetermined drop angle)
  - With argument: `drop(1500)` sets a specific PWM value

- `reset()`
  - Without argument: uses `RESET_PWM = 300` (predetermined reset angle)
  - With argument: `reset(300)` sets a specific PWM value

Edit the `DROP_PWM` and `RESET_PWM` constants in `dropper_wrapper.py` as needed.

### Notes

- Intended specifically for CaraCaras's dropper mechanism

### Status

- Current status: In testosterone
