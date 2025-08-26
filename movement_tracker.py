"""
Movement Tracker for Dermograph Application.
Processes IMU data and calculates 2D movement trajectory.
"""
import math
from typing import Dict, List, Tuple, Optional
import numpy as np
from utils import quaternion_to_euler, low_pass_filter, calculate_velocity_magnitude


class MovementTracker:
    """Tracks dermograph movement and calculates trajectory from IMU data."""
    
    def __init__(self, filter_alpha: float = 0.1):
        """
        Initialize the movement tracker.
        
        Args:
            filter_alpha: Low-pass filter coefficient (0-1)
        """
        self.filter_alpha = filter_alpha
        
        # Current state
        self.position = {'x': 0.0, 'y': 0.0}
        self.velocity = {'x': 0.0, 'y': 0.0}
        self.acceleration = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.orientation = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
        self.angular_velocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Filtered values
        self.filtered_accel = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.filtered_gyro = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Trajectory history
        self.trajectory = []
        self.max_trajectory_points = 5000  # Limit memory usage
        
        # Calibration and drift compensation
        self.gravity_compensation = True
        self.drift_reset_interval = 30.0  # seconds
        self.last_reset_time = 0.0
        self.velocity_threshold = 0.01  # m/s - below this, assume stationary
        
        # Statistics
        self.max_velocity = 0.0
        self.total_distance = 0.0
        self.last_position = {'x': 0.0, 'y': 0.0}
        
        # Timing
        self.last_timestamp = None
        self.dt = 0.01  # Default time step
        
    def reset(self):
        """Reset tracker state and clear trajectory."""
        self.position = {'x': 0.0, 'y': 0.0}
        self.velocity = {'x': 0.0, 'y': 0.0}
        self.acceleration = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.orientation = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
        self.angular_velocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        self.filtered_accel = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.filtered_gyro = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        self.trajectory = []
        self.max_velocity = 0.0
        self.total_distance = 0.0
        self.last_position = {'x': 0.0, 'y': 0.0}
        self.last_timestamp = None
        self.last_reset_time = 0.0
        
    def process_imu_sample(self, imu_data: Dict) -> Dict:
        """
        Process a single IMU sample and update trajectory.
        
        Args:
            imu_data: IMU data dictionary from simulator
            
        Returns:
            Processed movement data
        """
        timestamp = imu_data['timestamp']
        
        # Calculate time step
        if self.last_timestamp is not None:
            self.dt = timestamp - self.last_timestamp
        self.last_timestamp = timestamp
        
        # Extract data
        raw_accel = imu_data['linear_acceleration']
        raw_gyro = imu_data['angular_velocity']
        quaternion = imu_data['orientation']
        
        # Convert quaternion to Euler angles
        self.orientation = quaternion_to_euler(
            quaternion['x'], quaternion['y'], quaternion['z'], quaternion['w']
        )
        
        # Apply low-pass filtering to reduce noise
        self.filtered_accel['x'] = low_pass_filter(raw_accel['x'], self.filtered_accel['x'], self.filter_alpha)
        self.filtered_accel['y'] = low_pass_filter(raw_accel['y'], self.filtered_accel['y'], self.filter_alpha)
        self.filtered_accel['z'] = low_pass_filter(raw_accel['z'], self.filtered_accel['z'], self.filter_alpha)
        
        self.filtered_gyro['x'] = low_pass_filter(raw_gyro['x'], self.filtered_gyro['x'], self.filter_alpha)
        self.filtered_gyro['y'] = low_pass_filter(raw_gyro['y'], self.filtered_gyro['y'], self.filter_alpha)
        self.filtered_gyro['z'] = low_pass_filter(raw_gyro['z'], self.filtered_gyro['z'], self.filter_alpha)
        
        # Store current values
        self.acceleration = self.filtered_accel.copy()
        self.angular_velocity = self.filtered_gyro.copy()
        
        # Compensate for gravity and orientation if enabled
        if self.gravity_compensation:
            # Simple gravity compensation - subtract gravity component
            # In a real application, this would use proper coordinate transformation
            gravity_offset = 9.81
            self.acceleration['z'] -= gravity_offset
            
        # Integrate acceleration to get velocity (in 2D plane)
        # Use only X and Y components for 2D tracking
        self.velocity['x'] += self.acceleration['x'] * self.dt
        self.velocity['y'] += self.acceleration['y'] * self.dt
        
        # Apply velocity threshold to reduce drift when stationary
        vel_magnitude = calculate_velocity_magnitude(self.velocity['x'], self.velocity['y'])
        if vel_magnitude < self.velocity_threshold:
            self.velocity['x'] *= 0.9  # Gradual decay
            self.velocity['y'] *= 0.9
            
        # Integrate velocity to get position
        self.position['x'] += self.velocity['x'] * self.dt
        self.position['y'] += self.velocity['y'] * self.dt
        
        # Calculate distance traveled
        dx = self.position['x'] - self.last_position['x']
        dy = self.position['y'] - self.last_position['y']
        distance_increment = math.sqrt(dx * dx + dy * dy)
        self.total_distance += distance_increment
        self.last_position = self.position.copy()
        
        # Update maximum velocity
        if vel_magnitude > self.max_velocity:
            self.max_velocity = vel_magnitude
            
        # Periodic drift reset
        if timestamp - self.last_reset_time > self.drift_reset_interval:
            self._apply_drift_compensation()
            self.last_reset_time = timestamp
            
        # Create trajectory point
        trajectory_point = {
            'timestamp': timestamp,
            'position': self.position.copy(),
            'velocity': self.velocity.copy(),
            'acceleration': self.acceleration.copy(),
            'orientation': self.orientation.copy(),
            'angular_velocity': self.angular_velocity.copy(),
            'velocity_magnitude': vel_magnitude,
            'total_distance': self.total_distance,
            'z_acceleration': self.acceleration['z']  # For pressure indication
        }
        
        # Add to trajectory history
        self.trajectory.append(trajectory_point)
        
        # Limit trajectory length to prevent memory issues
        if len(self.trajectory) > self.max_trajectory_points:
            self.trajectory = self.trajectory[-self.max_trajectory_points:]
            
        return trajectory_point
        
    def _apply_drift_compensation(self):
        """Apply drift compensation to reduce accumulated errors."""
        # Simple velocity decay when low activity is detected
        recent_points = self.trajectory[-50:] if len(self.trajectory) >= 50 else self.trajectory
        
        if len(recent_points) < 10:
            return
            
        # Check if there's been little movement recently
        recent_velocities = [p['velocity_magnitude'] for p in recent_points]
        avg_velocity = sum(recent_velocities) / len(recent_velocities)
        
        if avg_velocity < self.velocity_threshold * 2:
            # Apply stronger decay if movement is minimal
            decay_factor = 0.7
            self.velocity['x'] *= decay_factor
            self.velocity['y'] *= decay_factor
            
    def get_current_state(self) -> Dict:
        """
        Get current tracker state.
        
        Returns:
            Dictionary with current state information
        """
        velocity_magnitude = calculate_velocity_magnitude(self.velocity['x'], self.velocity['y'])
        
        return {
            'position': self.position.copy(),
            'velocity': self.velocity.copy(),
            'acceleration': self.acceleration.copy(),
            'orientation': self.orientation.copy(),
            'angular_velocity': self.angular_velocity.copy(),
            'velocity_magnitude': velocity_magnitude,
            'max_velocity': self.max_velocity,
            'total_distance': self.total_distance,
            'trajectory_length': len(self.trajectory)
        }
        
    def get_trajectory(self, max_points: Optional[int] = None) -> List[Dict]:
        """
        Get trajectory points.
        
        Args:
            max_points: Maximum number of recent points to return
            
        Returns:
            List of trajectory points
        """
        if max_points is None:
            return self.trajectory.copy()
        else:
            return self.trajectory[-max_points:].copy()
            
    def get_trajectory_2d(self, max_points: Optional[int] = None) -> Tuple[List[float], List[float]]:
        """
        Get 2D trajectory coordinates for plotting.
        
        Args:
            max_points: Maximum number of recent points to return
            
        Returns:
            Tuple of (x_coordinates, y_coordinates)
        """
        trajectory = self.get_trajectory(max_points)
        
        x_coords = [point['position']['x'] for point in trajectory]
        y_coords = [point['position']['y'] for point in trajectory]
        
        return x_coords, y_coords
        
    def get_velocity_colors(self, max_points: Optional[int] = None) -> List[float]:
        """
        Get velocity magnitudes for color mapping in visualization.
        
        Args:
            max_points: Maximum number of recent points to return
            
        Returns:
            List of velocity magnitudes
        """
        trajectory = self.get_trajectory(max_points)
        return [point['velocity_magnitude'] for point in trajectory]
        
    def export_trajectory_data(self) -> List[Dict]:
        """
        Export trajectory data in a format suitable for saving.
        
        Returns:
            List of simplified trajectory points
        """
        export_data = []
        for point in self.trajectory:
            export_point = {
                'timestamp': point['timestamp'],
                'x': point['position']['x'],
                'y': point['position']['y'],
                'vx': point['velocity']['x'],
                'vy': point['velocity']['y'],
                'velocity_magnitude': point['velocity_magnitude'],
                'ax': point['acceleration']['x'],
                'ay': point['acceleration']['y'],
                'az': point['acceleration']['z'],
                'roll': point['orientation']['roll'],
                'pitch': point['orientation']['pitch'],
                'yaw': point['orientation']['yaw'],
                'total_distance': point['total_distance']
            }
            export_data.append(export_point)
            
        return export_data