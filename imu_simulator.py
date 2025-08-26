"""
IMU Data Simulator for Dermograph Tracking Application.
Generates realistic IMU data that simulates a Witmotion sensor.
"""
import time
import math
import random
from typing import Dict, List, Tuple, Optional
import numpy as np
from utils import apply_noise, euler_to_quaternion


class IMUSimulator:
    """Simulates IMU sensor data for dermograph movements."""
    
    def __init__(self, sample_rate: float = 100.0):
        """
        Initialize the IMU simulator.
        
        Args:
            sample_rate: Data generation frequency in Hz
        """
        self.sample_rate = sample_rate
        self.dt = 1.0 / sample_rate  # Time step
        
        # Current state
        self.time_start = time.time()
        self.current_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.current_velocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.current_orientation = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
        self.current_angular_velocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Movement pattern parameters
        self.pattern_type = 'demo'  # 'demo', 'random', 'replay'
        self.pattern_time = 0.0
        self.pattern_speed = 1.0
        
        # Noise parameters
        self.accel_noise_std = 0.02  # m/s²
        self.gyro_noise_std = 0.01   # rad/s
        self.mag_noise_std = 0.1     # µT
        
        # Bias and drift simulation
        self.accel_bias = {'x': 0.01, 'y': -0.005, 'z': 0.02}
        self.gyro_bias = {'x': 0.001, 'y': 0.002, 'z': -0.001}
        
        # Dermograph-specific parameters
        self.pressure_simulation = True
        self.base_pressure = 9.81  # Base Z acceleration (gravity)
        
    def set_mode(self, mode: str, speed: float = 1.0):
        """
        Set simulation mode.
        
        Args:
            mode: 'demo', 'random', or 'replay'
            speed: Speed multiplier for simulation
        """
        self.pattern_type = mode
        self.pattern_speed = speed
        self.pattern_time = 0.0
        
    def reset(self):
        """Reset simulator state."""
        self.time_start = time.time()
        self.current_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.current_velocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.current_orientation = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
        self.current_angular_velocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.pattern_time = 0.0
        
    def _generate_demo_movement(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Generate predefined dermograph movement patterns."""
        t = self.pattern_time * self.pattern_speed
        
        # Different patterns based on time progression
        pattern_duration = 10.0  # seconds for each pattern
        pattern_phase = (t % (pattern_duration * 4)) / pattern_duration
        
        if pattern_phase < 1.0:  # Straight lines
            accel_x = 0.5 * math.sin(t * 2)
            accel_y = 0.1 * math.cos(t * 3)
            angular_vel_z = 0.1 * math.sin(t)
            
        elif pattern_phase < 2.0:  # Circular motions
            freq = 2.0
            accel_x = 1.0 * math.cos(t * freq) * freq
            accel_y = 1.0 * math.sin(t * freq) * freq
            angular_vel_z = freq
            
        elif pattern_phase < 3.0:  # Figure-8 patterns
            freq = 1.5
            accel_x = 2.0 * math.cos(t * freq) * freq
            accel_y = 1.0 * math.sin(t * freq * 2) * freq * 2
            angular_vel_z = 0.5 * math.sin(t * freq)
            
        else:  # Dotted/stippling movements
            if int(t * 5) % 2 == 0:  # Rapid on/off
                accel_x = 2.0 * (random.random() - 0.5)
                accel_y = 2.0 * (random.random() - 0.5)
            else:
                accel_x = 0.0
                accel_y = 0.0
            angular_vel_z = 0.2 * (random.random() - 0.5)
        
        # Simulate pressure changes (Z acceleration)
        pressure_variation = 0.3 * math.sin(t * 8)  # Higher frequency pressure changes
        accel_z = pressure_variation
        
        # Angular velocities for roll and pitch (small values for stability)
        angular_vel_x = 0.05 * math.sin(t * 1.5)
        angular_vel_y = 0.03 * math.cos(t * 2.2)
        
        acceleration = {'x': accel_x, 'y': accel_y, 'z': accel_z}
        angular_velocity = {'x': angular_vel_x, 'y': angular_vel_y, 'z': angular_vel_z}
        
        return acceleration, angular_velocity
        
    def _generate_random_movement(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Generate random but realistic movements."""
        # Use Perlin-like noise for smooth random movements
        t = self.pattern_time * self.pattern_speed
        
        # Multiple frequency components for realistic movement
        accel_x = (0.8 * math.sin(t * 1.1 + 0.5) + 
                  0.3 * math.sin(t * 2.7 + 1.2) + 
                  0.1 * math.sin(t * 5.3 + 2.1))
        
        accel_y = (0.7 * math.cos(t * 1.3 + 1.1) + 
                  0.4 * math.cos(t * 2.1 + 0.8) + 
                  0.15 * math.cos(t * 4.7 + 1.7))
        
        # Random pressure variations
        accel_z = 0.4 * math.sin(t * 3.5 + random.random())
        
        # Smooth angular velocity changes
        angular_vel_x = 0.1 * math.sin(t * 1.7 + 0.3)
        angular_vel_y = 0.08 * math.cos(t * 1.9 + 0.9)
        angular_vel_z = 0.3 * math.sin(t * 1.5 + 0.6)
        
        acceleration = {'x': accel_x, 'y': accel_y, 'z': accel_z}
        angular_velocity = {'x': angular_vel_x, 'y': angular_vel_y, 'z': angular_vel_z}
        
        return acceleration, angular_velocity
    
    def _update_state(self, acceleration: Dict[str, float], angular_velocity: Dict[str, float]):
        """Update internal state based on acceleration and angular velocity."""
        # Update velocity (integrate acceleration)
        self.current_velocity['x'] += acceleration['x'] * self.dt
        self.current_velocity['y'] += acceleration['y'] * self.dt
        self.current_velocity['z'] += acceleration['z'] * self.dt
        
        # Update position (integrate velocity)
        self.current_position['x'] += self.current_velocity['x'] * self.dt
        self.current_position['y'] += self.current_velocity['y'] * self.dt
        self.current_position['z'] += self.current_velocity['z'] * self.dt
        
        # Update orientation (integrate angular velocity)
        self.current_orientation['roll'] += math.degrees(angular_velocity['x']) * self.dt
        self.current_orientation['pitch'] += math.degrees(angular_velocity['y']) * self.dt
        self.current_orientation['yaw'] += math.degrees(angular_velocity['z']) * self.dt
        
        # Keep angles in reasonable range
        for axis in ['roll', 'pitch', 'yaw']:
            while self.current_orientation[axis] > 180:
                self.current_orientation[axis] -= 360
            while self.current_orientation[axis] < -180:
                self.current_orientation[axis] += 360
                
        # Store current angular velocity
        self.current_angular_velocity = angular_velocity.copy()
        
        # Apply velocity damping to prevent unrealistic drift
        damping = 0.99
        for axis in ['x', 'y', 'z']:
            self.current_velocity[axis] *= damping
    
    def generate_sample(self) -> Dict[str, any]:
        """
        Generate a single IMU data sample.
        
        Returns:
            Dictionary containing IMU data in the specified format
        """
        current_time = time.time()
        
        # Generate movement based on current mode
        if self.pattern_type == 'demo':
            raw_accel, raw_angular_vel = self._generate_demo_movement()
        elif self.pattern_type == 'random':
            raw_accel, raw_angular_vel = self._generate_random_movement()
        else:  # replay mode would be implemented separately
            raw_accel = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            raw_angular_vel = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Add bias and noise
        acceleration = {
            'x': apply_noise(raw_accel['x'] + self.accel_bias['x'], self.accel_noise_std),
            'y': apply_noise(raw_accel['y'] + self.accel_bias['y'], self.accel_noise_std),
            'z': apply_noise(raw_accel['z'] + self.accel_bias['z'] + self.base_pressure, self.accel_noise_std)
        }
        
        angular_velocity = {
            'x': apply_noise(raw_angular_vel['x'] + self.gyro_bias['x'], self.gyro_noise_std),
            'y': apply_noise(raw_angular_vel['y'] + self.gyro_bias['y'], self.gyro_noise_std),
            'z': apply_noise(raw_angular_vel['z'] + self.gyro_bias['z'], self.gyro_noise_std)
        }
        
        # Update internal state
        self._update_state(raw_accel, raw_angular_vel)
        
        # Generate orientation quaternion
        quaternion = euler_to_quaternion(
            self.current_orientation['roll'],
            self.current_orientation['pitch'], 
            self.current_orientation['yaw']
        )
        
        # Generate magnetic field (simplified - just add noise to nominal values)
        magnetic_field = {
            'x': apply_noise(22.0, self.mag_noise_std),  # Approximate Earth's magnetic field
            'y': apply_noise(5.0, self.mag_noise_std),
            'z': apply_noise(-42.0, self.mag_noise_std)
        }
        
        # Update pattern time
        self.pattern_time += self.dt
        
        # Return data in specified format
        return {
            'timestamp': current_time,
            'linear_acceleration': acceleration,
            'angular_velocity': angular_velocity,
            'orientation': quaternion,
            'magnetic_field': magnetic_field,
            # Additional computed values for convenience
            'position': self.current_position.copy(),
            'velocity': self.current_velocity.copy(),
            'euler_angles': self.current_orientation.copy()
        }