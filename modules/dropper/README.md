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
- Call `drop()` to activate the dropper mechanism

- Dropper firmware will receive serial commands corresponding to wrapper function calls and execute the matching actuator behavior on the STM32
    - Commands:
        - Drop: "D\n"
        - Reset: "R\n"

### Notes

- Intended specifically for CaraCaras's dropper mechanism

### Status

- Current status: Ready for Approval
