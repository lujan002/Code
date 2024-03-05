Code and 3D models for a robotic arm I developed using Arduino Uno and ESP32 bluetooth module. 

Original 3D Models and information about the EEZYbotARM-Mk2 can be found here: http://www.eezyrobots.it/eba_mk2.html 
I ended up swapping the gripper out for a different gripper which was larger and stronger

Watch documentation in this video: https://youtu.be/VW5HBfSHOiM 

Find the Receive_Data.ino file inside PS4-esp32-master.zip

Steps to control arm using PS4 and ESP32. 
1. Make sure “ESP32 Dev Module” is the board being used and it is plugged in and connected over COM port
2. Upload control_servo_serial.ino to Ardunio UNO on separate COM port
3. Upload Receive_Data.ino to ESP32 on COM port. Hold down BOOT/GPIO 100 button when “Conecting…” appears in the serial monitor. 
4. Run the robot_arm_esp32_control.py script (make sure to change your COM ports to your respective setup)
5. You should see “ready” in the output window. Press the “EN” (enable) button on the ESP32 and then press the home button on PS4 Controller. Move the joysticks and it should work. 
6. If it says something like “COM port unavailable” unplug both the arduino and ESP32, and try again from step 1. 
Sometimes after changing the controller Mac address or connecting the controller to a PS4 and changing the Mac address back, the ESP32 won’t recognize the controller. If that happens, follow this article: https://randomnerdtutorials.com/esp32-erase-flash-memory/ to fix.


I labeled the servos to keep track. Servo 1 controls the lower arm, Servo 2 controls the upper arm, servo 3 rotates the base, and servo 4 opens the gripper.
The limits for servo 2 interestingly depend on the position of servo 1. When servo 1 is near the limits of its range, that is when the main arm is fully extended or contracted, servo 2 cannot move through its full range of motion. I made a rough note of a few of servo 2’s limits based on servo 1 angles and approximated a linear fit for this relationship. An easy way to test this relationship with your setup is to use the servo_sliders.py script I created. This lets you control each servo individually using a slider GUI. You may need to adjust the slider bounds to corespond to your servo setup. 

Having a slider control each arm works, but it’s a bit clunky if you want to move the end effector up or down, since both servo 1 and 2 influence its x-y position. I want a setup that has three sliders, one for x, y, and rotation. This requires calculating the inverse kinematics, or the conversion of an x-y coordinate to arm angles. To do that I had to measure the arm angles. I found this video online which was very helpful: https://robotacademy.net.au/lesson/inverse-kinematics-for-a-2-joint-robot-arm-using-geometry/. (Note: the video measures the angle of arm 2 relative to arm 1. This is correct for a normal 2 bar robot arm where arm two is driven by the motor in the elbow where arm 1 and 2 connect, as is common on many robotic arms. The problem with my robot is that there is this special arm that actually prevents arm 2 from rotating with arm 1, so I was running into this issue where arm 2 was trying to compensate for this to keep level even though it didn’t need to. Changing the arm 2 angles to be measured to the ground instead fixed this issue)

I made inverse_kinematics_plot.py to simulate what the robot arm should look like based on my x-y coordinate input. I compared this to my physical robot to help me refine my inverse kinematics. 

To control the robot using a PS4 controller, I used a ESP32 bluetooth module. The first step was to set the PS4 and ESP32 to have the same Bluetooth address so they could communicate. I did this using software called sixaxispair tool. I can upload code to the ESP32 through the ardunio IDE just like with an Arduino board. 

How it works, broadly speaking: 
PS4 talks to the ESP32 over Bluetooth, ESP32 receives joystick inputs
ESP32 sends inputs over the serial port to my computer where a python script is running
In the python script, the joystick inputs are read, normalized (converted to value between 0-1), converted to a delta value, and added to the last coordinate value
This effectively gives us x,y,rotation coordinates, which are first fed through a function which checks if they are in the robot’s range of motion
Then inverse kinematics are calculated, outputing arm angles
Arm angles are mapped to the servo angles based on my setup
Modified angle values are encoded into a one-line string (to speed up data transfer) and sent to Arduino over a second serial port
Arduino decodes the string and writes values to servos




