# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 09:24:17 2024

@author: 20Jan
"""

import matplotlib.pyplot as plt
import numpy as np

def calculate_servo2_range(theta1):
    # Adjust these values based on the exact relationship you have between servo angles and "true" angles 
    if 102 <= theta1 <= 131:
        # Linearly interpolate servo2's range
        min_theta2 = -127.5  # Assuming this is the start range and does not change
        max_theta2 = np.interp(theta1, [102, 131], [-71, -127.5])  # Linearly interpolates based on theta1
    elif 61.25 <= theta1 < 102:
        # Constant range for Servo 2
        min_theta2 = -158
        max_theta2 = -71
    elif 38 <= theta1 < 61.25:
        # Linearly interpolate servo2's range
        min_theta2 = np.interp(theta1, [38, 61.25], [-158, -158])  # Assuming start range does not change
        max_theta2 = np.interp(theta1, [38, 61.25], [-88.4, -71])  # Linearly interpolates based on theta1
    else:
        # Default case, might need adjustments or error handling
        min_theta2 = -158
        max_theta2 = -71
    return min_theta2, max_theta2

# Function to calculate the inverse kinematics
def inverse_kinematics(x, y, a1, a2):
    r1 = np.sqrt(x**2 + y**2)
    q2 = -np.arccos((r1**2 - a1**2 - a2**2) / (2 * a1 * a2))
    q1 = np.arctan2(y, x) - np.arctan2((a2 * np.sin(q2)), (a1 + a2 * np.cos(q2)))
    return np.rad2deg(q1), np.rad2deg(q2)

# Function to calculate the position of the end of each arm
def calculate_positions(a1, a2, theta1, theta2):
    theta1_rad = np.deg2rad(theta1)
    theta2_rad = np.deg2rad(theta2 + theta1)  # theta2 is relative to the end of arm1
    x1 = a1 * np.cos(theta1_rad)
    y1 = a1 * np.sin(theta1_rad)
    x2 = x1 + a2 * np.cos(theta2_rad)
    y2 = y1 + a2 * np.sin(theta2_rad)
    return (x1, y1), (x2, y2)

# Function to draw the robot arm with updated servo angles
def plot_robot_arm_with_angles(x, y, a1, a2):
    # Calculate the servo angles from x, y
    theta1, theta2 = inverse_kinematics(x, y, a1, a2)
    # Calculate Servo 2's dynamic range based on Servo 1's position
    servo2_min, servo2_max = calculate_servo2_range(theta1)
    # Calculate arm positions
    (x1, y1), (x2, y2) = calculate_positions(a1, a2, theta1, theta2)
    # Start plotting
    fig, ax = plt.subplots()
    # If either Servo is out of bounds, print an error
    if not 38 <= theta1 <= 131:
        print(f"Error: Servo1 angle {theta1} is out of range.")
        ax.plot([0, x1, x2], [0, y1, y2], 'ko-', linewidth=6, markersize=12, color='red') # Plot the arms red showing error   
    elif not servo2_min <= theta2 <= servo2_max:
        print(f"Error: Servo2 angle {theta2} is out of range. Valid range: {servo2_min} to {servo2_max}.")
        ax.plot([0, x1, x2], [0, y1, y2], 'ko-', linewidth=6, markersize=12, color='red') # Plot the arms red showing error
    else:
        print('Servo1 angle:', theta1)
        print('Servo2 angle:', theta2, f"(Range: {servo2_min} to {servo2_max})")
        ax.plot([0, x1, x2], [0, y1, y2], 'ko-', linewidth=6, markersize=12) # Plot the arms    
    # Plot the servo angles as text
    ax.text(0, 0, f'{theta1:.1f}°', fontsize=12, verticalalignment='bottom', horizontalalignment='right')
    ax.text(x1, y1, f'{theta2:.1f}°', fontsize=12, verticalalignment='bottom', horizontalalignment='right')
    # Set the aspect of the plot to be equal
    ax.set_aspect('equal')
    # Set grid
    ax.grid(True)
    # Set the plot limits
    ax.set_xlim(-a1-a2, a1+a2)
    ax.set_ylim(-a1-a2, a1+a2)
    # Add title and labels
    ax.set_title('Robot Arm Position')
    ax.set_xlabel('X coordinate (mm)')
    ax.set_ylabel('Y coordinate (mm)')
    # Show plot
    plt.show()

# Constants for arm lengths
a1 = 130  # length of arm1 in mm
a2 = 151  # length of arm2 in mm

# Desired position of the end effector
x = 100  # x-coordinate
y = 100  # y-coordinate

# Plot the robot arm with the calculated angles for the given x, y position
plot_robot_arm_with_angles(x, y, a1, a2)

