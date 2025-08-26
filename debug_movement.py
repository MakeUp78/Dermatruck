#!/usr/bin/env python3
"""
Debug script to check movement generation.
"""
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from imu_simulator import IMUSimulator
from movement_tracker import MovementTracker

def debug_movement():
    print("Debugging movement generation...")
    
    sim = IMUSimulator(sample_rate=20.0)
    tracker = MovementTracker()
    
    # Run a short simulation
    sim.set_mode('demo', speed=2.0)
    
    positions = []
    for i in range(20):
        imu_data = sim.generate_sample()
        trajectory_point = tracker.process_imu_sample(imu_data)
        pos = trajectory_point['position']
        positions.append((pos['x'], pos['y']))
        print(f"Step {i+1}: Position ({pos['x']:.4f}, {pos['y']:.4f}), "
              f"Accel ({imu_data['linear_acceleration']['x']:.3f}, {imu_data['linear_acceleration']['y']:.3f})")
        
        time.sleep(0.01)
        
    # Check for movement
    max_x = max(pos[0] for pos in positions)
    min_x = min(pos[0] for pos in positions)
    max_y = max(pos[1] for pos in positions)
    min_y = min(pos[1] for pos in positions)
    
    x_range = max_x - min_x
    y_range = max_y - min_y
    
    print(f"\nMovement analysis:")
    print(f"X range: {x_range:.6f} m (from {min_x:.6f} to {max_x:.6f})")
    print(f"Y range: {y_range:.6f} m (from {min_y:.6f} to {max_y:.6f})")
    print(f"Total movement: {max(x_range, y_range):.6f} m")
    
    if max(x_range, y_range) > 0.01:
        print("✓ Significant movement detected")
        return True
    else:
        print("✗ No significant movement detected")
        return False

if __name__ == "__main__":
    debug_movement()