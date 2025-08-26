"""
Utility functions for the dermograph tracking application.
"""
import json
import csv
import math
from typing import Dict, List, Any
import numpy as np


def quaternion_to_euler(x: float, y: float, z: float, w: float) -> Dict[str, float]:
    """
    Convert quaternion to euler angles (roll, pitch, yaw) in degrees.
    
    Args:
        x, y, z, w: Quaternion components
        
    Returns:
        Dictionary with roll, pitch, yaw in degrees
    """
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    
    # Pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)
    
    # Yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    
    # Convert to degrees
    return {
        'roll': math.degrees(roll),
        'pitch': math.degrees(pitch),
        'yaw': math.degrees(yaw)
    }


def euler_to_quaternion(roll: float, pitch: float, yaw: float) -> Dict[str, float]:
    """
    Convert euler angles (in degrees) to quaternion.
    
    Args:
        roll, pitch, yaw: Euler angles in degrees
        
    Returns:
        Dictionary with quaternion components x, y, z, w
    """
    # Convert to radians
    roll_rad = math.radians(roll)
    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)
    
    cy = math.cos(yaw_rad * 0.5)
    sy = math.sin(yaw_rad * 0.5)
    cp = math.cos(pitch_rad * 0.5)
    sp = math.sin(pitch_rad * 0.5)
    cr = math.cos(roll_rad * 0.5)
    sr = math.sin(roll_rad * 0.5)
    
    w = cy * cp * cr + sy * sp * sr
    x = cy * cp * sr - sy * sp * cr
    y = sy * cp * sr + cy * sp * cr
    z = sy * cp * cr - cy * sp * sr
    
    return {'x': x, 'y': y, 'z': z, 'w': w}


def apply_noise(value: float, noise_std: float = 0.01) -> float:
    """
    Add Gaussian noise to a value.
    
    Args:
        value: Original value
        noise_std: Standard deviation of noise
        
    Returns:
        Value with added noise
    """
    return value + np.random.normal(0, noise_std)


def low_pass_filter(new_value: float, old_value: float, alpha: float = 0.1) -> float:
    """
    Apply simple low-pass filter to reduce noise.
    
    Args:
        new_value: New measurement
        old_value: Previous filtered value
        alpha: Filter coefficient (0-1, lower = more smoothing)
        
    Returns:
        Filtered value
    """
    return alpha * new_value + (1 - alpha) * old_value


def save_trajectory_csv(trajectory: List[Dict], filename: str) -> bool:
    """
    Save trajectory data to CSV file.
    
    Args:
        trajectory: List of trajectory points
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', newline='') as csvfile:
            if not trajectory:
                return False
                
            fieldnames = trajectory[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(trajectory)
            return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False


def save_trajectory_json(trajectory: List[Dict], filename: str) -> bool:
    """
    Save trajectory data to JSON file.
    
    Args:
        trajectory: List of trajectory points
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as jsonfile:
            json.dump(trajectory, jsonfile, indent=2)
            return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False


def load_trajectory_json(filename: str) -> List[Dict]:
    """
    Load trajectory data from JSON file.
    
    Args:
        filename: Input filename
        
    Returns:
        List of trajectory points, empty list if error
    """
    try:
        with open(filename, 'r') as jsonfile:
            return json.load(jsonfile)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return []


def calculate_velocity_magnitude(vx: float, vy: float) -> float:
    """
    Calculate 2D velocity magnitude.
    
    Args:
        vx, vy: Velocity components
        
    Returns:
        Velocity magnitude
    """
    return math.sqrt(vx * vx + vy * vy)


def normalize_angle(angle: float) -> float:
    """
    Normalize angle to [-180, 180] degrees.
    
    Args:
        angle: Input angle in degrees
        
    Returns:
        Normalized angle
    """
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle