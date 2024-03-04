


# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 12:50:00 2024

@author: 20Jan
"""

# import matplotlib.pyplot as plt
import numpy as np
# import tkinter as tk
# from tkinter import ttk
import serial
import threading
import time
from queue import Queue

# Connect to ESP32
esp32 = serial.Serial('COM6', 115200, timeout=1)
time.sleep(2)  # wait for the serial connection to initialize
esp32.flushInput()  # Flush startup text or any other data in the buffer

# Connect to Arduino
arduino = serial.Serial('COM4', 9600)  # Replace 'COM_Arduino' with the actual COM port
time.sleep(2) # wait for the serial connection to initialize

# Create a queue that will be used to pass data from the reading thread to the processing thread
data_queue = Queue()

def read_from_esp32():
    while True:
        if esp32.in_waiting > 0:
            line = esp32.readline().decode('utf-8').rstrip()
            data_queue.put(line)  # Put the raw line into the queue for processing
            #print(line)
            print('hi')
            
def process_data():
    
    while True:
        line = data_queue.get()  # Wait for data from the queue
        # Split the line by commas
        parts = line.split(',')
        values = []
        for part in parts:
            try:
                # Try converting each part to float and add to the values list
                values.append(float(part))
            except ValueError:
                # If conversion fails, it's not a float, skip this part
                continue
        print(values)
        # Now, values contains only the successfully converted floats
        if len(values) >= 4:  # Check if we have at least 4 values
            x, y = values[0], values[3]
            z = values[13]-values[12]
            g = values[14]-values[15]
            # x = values[3]
            # y = values[13]-values[12]
            # z = values[0]
            # g = values[14]-values[15]
            process_joystick_input(x,y,z,g)       
            # Proceed with using theta1, theta2 for plotting or sending to Arduino
            # Remember to ensure these operations are non-blocking
        else:
            print(f"Not enough valid numeric data received: {line}")
          
        data_queue.task_done()  # Signal that the processing is complete

# Initial position of the robot arm
current_x = 100  # Adjust these values based on your robot arm's default position
current_y = 100
current_z = 90  
current_g = 50

# Define limits for robot arm range
x_min, x_max = 50, 230  
y_min, y_max = -80, 120
z_min, z_max = 0, 180
g_min, g_max = 5, 95

def process_joystick_input(x, y, z, g):
    global current_x, current_y, current_z, current_g

    # Convert joystick input to movement deltas
    # This conversion will depend on how your joystick inputs are scaled
    # and how sensitive you want the controls to be
    delta_x = convert_joystick_to_delta(x)
    delta_y = convert_joystick_to_delta(y)
    # Multiply binary trigger value by 5 to speed up movement (binary equivalent of convert_joystick_to_delta)
    delta_z = z * 5 
    delta_g = g * 5
    # Calculate the new proposed position
    new_x = current_x + delta_x
    new_y = current_y + delta_y
    new_z = current_z + delta_z
    new_g = current_g + delta_g
    # Enforce x limits
    if new_x < x_min:
        new_x = x_min
    elif new_x > x_max:
        new_x = x_max
    # Enforce y limits
    if new_y < y_min:
        new_y = y_min
    elif new_y > y_max:
        new_y = y_max
    # Enforce z limits
    if new_z < z_min:
        new_z = z_min
    elif new_z > z_max:
        new_z = z_max
    # Enforce g limits     
    if new_g < g_min:
        new_g = g_min
    elif new_g > g_max:
        new_g = g_max
    # Enforce limits for lower corner 
    if new_x < 160 and new_y < 15:
        new_x = 160
        new_y = 15        
    # Update the current position to the new, valid position
    current_x, current_y, current_z, current_g = new_x, new_y, new_z, new_g
    print('current x: ', current_x)
    print('current y: ', current_y)
    # Now current_x and current_y hold the new desired position of the robot arm
    # Continue with sending this new position to the robot arm
    theta1, theta2 = inverse_kinematics(current_x, current_y, a1, a2)
    theta3, theta4 = current_z, current_g
    send_to_arduino(theta1, theta2, theta3, theta4)       
    
# Dead zone threshold
dead_zone_threshold = 5  # Adjust based on your joystick's sensitivity

def convert_joystick_to_delta(joystick_value):
    # If joystick value is within the dead zone, treat it as 0 (no movement)
    if -dead_zone_threshold <= joystick_value <= dead_zone_threshold:
        return 0
    # Otherwise, proceed with converting the joystick value to a movement delta
    joystick_value_scaled = joystick_value/127
    max_delta = 5.0  # Maximum change per input, adjust as needed
    return joystick_value_scaled * max_delta

# Function to update the label and send data to Arduino
# def update_label_x(slider_x, label_x):
#     x = slider_x.get()
#     label_x.config(text=f"Value: {x}")
#     y = slider2.get()  # Get the current value of y from slider2
#     # Plot the robot arm with the calculated angles for the given x, y position
#     plot_robot_arm_with_angles(x, y, a1, a2)

# def update_label_y(slider_y, label_y):
#     y = slider_y.get()
#     label_y.config(text=f"Value: {y}")
#     x = slider1.get()  # Get the current value of x from slider1
#     # Plot the robot arm with the calculated angles for the given x, y position
#     plot_robot_arm_with_angles(x, y, a1, a2)
    
# Function to send all values to Arduino
def send_to_arduino(theta1, theta2, theta3, theta4):
    #calculate s2 range in global coordinate frame 
    s2_max = 19 #19
    s2_min = -69 #-69
    # Convert the "global" angles into Arunino Servo angles by interpolation
    theta1_mod = ((theta1-s1_min)/(s1_max-s1_min))*(-s1_mod_max+s1_mod_min)+s1_mod_max
    theta2_mod = ((theta2-s2_max)/(s2_min-s2_max))*(-s2_mod_max+s2_mod_min)+s2_mod_max
    print('theta1_mod:',theta1_mod)
    print('theta2_mod:',theta2_mod)
    print('theta3:',theta3)
    print('theta4:',theta4)
    data_string = f"{theta1_mod},{theta2_mod},{theta3},{theta4}\n"  # Format to be parsed by Arduino
    #print(f"Sending to Arduino: {data_string}") # Debugging 
    arduino.write(data_string.encode())
    
# def calculate_servo2_range(theta1):
#     #calculate s2 range in global coordinate frame 
#     s2_max = 19 #19
#     s2_min = -69 #-69
#     # Adjust these values based on the exact relationship you have
#     if 102 <= theta1 <= s1_max:
#         # Linearly interpolate servo2's range
#         min_theta2 = -127.5+theta1  # Assuming this is the start range and does not change
#         max_theta2 = np.interp(theta1, [102, s1_max], [s2_max, -127.5])+theta1  # Linearly interpolates based on theta1
#     elif 61.25 <= theta1 < 102:
#         # Constant range for Servo 2
#         min_theta2 = s2_min
#         max_theta2 = s2_max
#     elif s1_min <= theta1 < 61.25:
#         # Linearly interpolate servo2's range
#         min_theta2 = np.interp(theta1, [s1_min, 61.25+theta1], [s2_min, s2_min])  # Assuming start range does not change
#         max_theta2 = np.interp(theta1, [s1_min, 61.25+theta1], [-88.4+theta1, s2_max])  # Linearly interpolates based on theta1
#     else:
#         # Default case, might need adjustments or error handling
#         min_theta2 = s2_min
#         max_theta2 = s2_max
#     return min_theta2, max_theta2

# Function to calculate the inverse kinematics
# def inverse_kinematics(x, y, a1, a2):
#     r1 = np.sqrt(x**2 + y**2)
#     q2 = -np.arccos((r1**2 - a1**2 - a2**2) / (2 * a1 * a2))
#     q1 = np.arctan2(y, x) - np.arctan2((a2 * np.sin(q2)), (a1 + a2 * np.cos(q2)))
#     # Set theta2 to global coordinates
#     q2 = q2 + q1 
#     print("theta1: ", q1)
#     print("theta2: ", q2)
#     # send_to_arduino(q1, q2)
#     # return np.rad2deg(q1), np.rad2deg(q2)

# Initialize global variables for the last valid x and y for error handling 
last_valid_x = 100
last_valid_y = 100

def inverse_kinematics(x, y, a1, a2): # with error handling
    global last_valid_x, last_valid_y
    
    r1 = np.sqrt(x**2 + y**2)
    if r1 > a1 + a2 or r1 < np.abs(a1 - a2):
        # Point is outside the reachable workspace
        print(f"Error: Target point ({x}, {y}) is outside of the reachable workspace.")
        if last_valid_x is None or last_valid_y is None:
            # If there are no last valid values, return None
            return None, None
        else:
            # Use the last valid x and y if available
            # If an x-y combination outside the target range is passed, this handles the error
            x, y = last_valid_x, last_valid_y
            print(f"Using last valid point: ({x}, {y})")
    else:
        # Update the last valid x and y
        last_valid_x, last_valid_y = x, y

    # Proceed with the calculations using x and y (which may be the last valid values)
    r1 = np.sqrt(x**2 + y**2)  # Recalculate r1 in case last valid values are used
    argument = (r1**2 - a1**2 - a2**2) / (2 * a1 * a2)
    if argument < -1 or argument > 1:
        print(f"Error: arccos argument out of range: {argument}")
        return None, None

    q2 = -np.arccos(argument)
    q1 = np.arctan2(y, x) - np.arctan2((a2 * np.sin(q2)), (a1 + a2 * np.cos(q2)))
    q2 = q2 + q1  # Set theta2 to global coordinates
    q1 = np.rad2deg(q1)
    q2 = np.rad2deg(q2) 
    print("theta1: ", q1)
    print("theta2: ", q2)
    return q1, q2

# Function to calculate the position of the end of each arm
# def calculate_positions(a1, a2, theta1, theta2):
#     theta1_rad = np.deg2rad(theta1)
#     theta2_rad = np.deg2rad(theta2) #+ theta1)  # theta2 is relative to the end of arm1
#     x1 = a1 * np.cos(theta1_rad)
#     y1 = a1 * np.sin(theta1_rad)
#     x2 = x1 + a2 * np.cos(theta2_rad)
#     y2 = y1 + a2 * np.sin(theta2_rad)
#     return (x1, y1), (x2, y2)

# Function to draw the robot arm with updated servo angles
# def plot_robot_arm_with_angles(theta1, theta2):
#     # Calculate the servo angles from x, y
#     # theta1, theta2 = inverse_kinematics(x, y, a1, a2)
#     # Set theta2 to global coordinates
#     # theta2 = theta2 + theta1
#     print(theta1)
#     print(theta2)
#     # Calculate Servo 2's dynamic range based on Servo 1's position
#     servo2_min, servo2_max = calculate_servo2_range(theta1)
#     # Calculate arm positions
#     (x1, y1), (x2, y2) = calculate_positions(a1, a2, theta1, theta2)
#     # Start plotting
#     fig, ax = plt.subplots()
#     # If either Servo is out of bounds, print an error
#     if not s1_min <= theta1 <= s1_max:
#         print(f"Error: Servo1 angle {theta1} is out of range.")
#         ax.plot([0, x1, x2], [0, y1, y2], 'ko-', linewidth=6, markersize=12, color='red') # Plot the arms red showing error   
#     elif not servo2_min <= theta2 <= servo2_max:
#         print(f"Error: Servo2 angle {theta2} is out of range. Valid range: {servo2_min} to {servo2_max}.")
#         ax.plot([0, x1, x2], [0, y1, y2], 'ko-', linewidth=6, markersize=12, color='red') # Plot the arms red showing error
#     else:
#         print('Servo1 angle:', theta1)
#         print('Servo2 angle:', theta2, f"(Range: {servo2_min} to {servo2_max})")
#         ax.plot([0, x1, x2], [0, y1, y2], 'ko-', linewidth=6, markersize=12) # Plot the arms    
#     # Plot the servo angles as text
#     ax.text(0, 0, f'{theta1:.1f}°', fontsize=12, verticalalignment='bottom', horizontalalignment='right')
#     ax.text(x1, y1, f'{theta2:.1f}°', fontsize=12, verticalalignment='bottom', horizontalalignment='right')
#     # Set the aspect of the plot to be equal
#     ax.set_aspect('equal')
#     # Set grid
#     ax.grid(True)
#     # Set the plot limits
#     ax.set_xlim(-a1-a2, a1+a2)
#     ax.set_ylim(-a1-a2, a1+a2)
#     # Add title and labels
#     ax.set_title('Robot Arm Position')
#     ax.set_xlabel('X coordinate (mm)')
#     ax.set_ylabel('Y coordinate (mm)')
#     # Show plot
#     #plt.show()
#     #plt.ion() #this is supposedly better for real-time plot updating
#     # Send theta1, theta2 to Arduino over serial
#     send_to_arduino(theta1, theta2)


# Constants for arm lengths
a1 = 134.9  # length of arm1 in mm
a2 = 147.1  # length of arm2 in mm

# Constants for arm range of motion (global)
s1_min = 35
s1_max = 133 #133
    # define s2_min, s2_max in functions bc it depends on theta1

# Constants for arm range of motion (Ardunio Servo)
s1_mod_min = 0
s1_mod_max = 70
s2_mod_min = 45
s2_mod_max = 145

# Create the main window
# root = tk.Tk()
# root.title("X-Y Control")

# # Create the first slider for x
# slider1 = ttk.Scale(root, from_=0, to=200, orient='horizontal')
# slider1.pack()
# slider1.set(144)
# label1 = tk.Label(root, text="Value: 100")  # Initial value should match slider1.set()
# label1.pack()
# slider1.bind("<Motion>", lambda event: update_label_x(slider1, label1))

# # Create the second slider for y
# slider2 = ttk.Scale(root, from_=-150, to=200, orient='horizontal')
# slider2.pack()
# slider2.set(135)
# label2 = tk.Label(root, text="Value: 100")  # Initial value should match slider2.set()
# label2.pack()
# slider2.bind("<Motion>", lambda event: update_label_y(slider2, label2))

# # Run the Tkinter application
# root.mainloop()

# Start the thread to read from ESP32
threading.Thread(target=read_from_esp32, daemon=True).start()

# Start the thread to process data from the queue
threading.Thread(target=process_data, daemon=True).start()