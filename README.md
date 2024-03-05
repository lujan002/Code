# Robotic Arm Control Using PS4

This repository contains code and 3D models for a robotic arm developed using Arduino Uno and ESP32 Bluetooth module.

## Original 3D Models and Information
- Original 3D Models and information about the EEZYbotARM-Mk2 4 DoF robotic arm can be found [here](http://www.eezyrobots.it/eba_mk2.html).
- The gripper used in this project was swapped out for a larger and stronger one. If you wish to use this, find under 3D Models.
   
## Documentation
- Watch the documentation video [here](https://youtu.be/VW5HBfSHOiM).

## Instructions
### Controlling the Arm
1. Find the `Receive_Data.ino` file inside `PS4-esp32-master.zip`.
2. Make sure "ESP32 Dev Module" is selected as the board in Arduino IDE.
3. Upload `control_servo_serial.ino` to Arduino Uno.
4. Upload `Receive_Data.ino` to ESP32. Hold down BOOT/GPIO 100 button when "Connecting..." appears in the serial monitor.
5. Run the `robot_arm_esp32_control.py` script (ensure to change COM ports as per your setup).
6. Check for "ready" in the output window. If not immediately appearing, press the "EN" (enable) button on ESP32.
8. Press the home button on the PS4 Controller and move the joysticks to control the arm.

### Troubleshooting
- If "COM port unavailable" error occurs, unplug both Arduino and ESP32 and retry from Software Setup step 3.
- If ESP32 doesn't recognize the controller, follow [this article](https://randomnerdtutorials.com/esp32-erase-flash-memory/) to fix.

## Servo Labeling
- Servo 1: Controls the lower arm.
- Servo 2: Controls the upper arm.
- Servo 3: Rotates the base.
- Servo 4: Opens the gripper.

## Servo Limits
- Servo 2's limits depend on Servo 1's position.
- Use `servo_sliders.py` script to test this relationship.

## Inverse Kinematics
- Inverse kinematics is calculated for converting x-y coordinates to arm angles. [This](https://robotacademy.net.au/lesson/inverse-kinematics-for-a-2-joint-robot-arm-using-geometry/) video offers a helpful tutorial.
- Check `inverse_kinematics_plot.py` for simulation and refinement of inverse kinematics.

## PS4 Controller Integration
- ESP32 Bluetooth module is used for PS4 controller integration.
- Use sixaxispair tool to set PS4 and ESP32 to the same Bluetooth address.

## How it Works
- PS4 communicates with ESP32 over Bluetooth.
- ESP32 receives joystick inputs and sends them over serial to the computer.
- Python script reads, normalizes, and converts inputs to delta values.
- Inverse kinematics are calculated, and arm angles are mapped to servo angles.
- Modified angle values are encoded into a one-line string and sent to Arduino over serial.
- Arduino decodes the string and writes values to servos.

Feel free to explore and contribute to this project!



