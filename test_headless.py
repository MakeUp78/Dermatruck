#!/usr/bin/env python3
"""
Test the main application without GUI to verify everything works.
"""
import sys
import os
import time
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from imu_simulator import IMUSimulator
from movement_tracker import MovementTracker
from visualizer import DermographVisualizer

def test_headless_simulation():
    """Test the core simulation without GUI."""
    print("Testing headless simulation...")
    
    # Initialize components
    simulator = IMUSimulator(sample_rate=20.0)
    tracker = MovementTracker()
    
    # Set to demo mode
    simulator.set_mode('demo', speed=3.0)
    
    print("Running simulation for 5 seconds...")
    start_time = time.time()
    sample_count = 0
    
    while time.time() - start_time < 5.0:
        # Generate IMU data
        imu_data = simulator.generate_sample()
        
        # Process through tracker
        trajectory_point = tracker.process_imu_sample(imu_data)
        
        sample_count += 1
        
        # Print periodic updates
        if sample_count % 20 == 0:
            pos = trajectory_point['position']
            vel = trajectory_point['velocity_magnitude']
            print(f"Sample {sample_count}: Pos({pos['x']:.4f}, {pos['y']:.4f}), Vel {vel:.4f} m/s")
        
        time.sleep(1.0 / simulator.sample_rate)
    
    # Get final statistics
    state = tracker.get_current_state()
    trajectory = tracker.get_trajectory()
    
    print(f"\nSimulation complete!")
    print(f"Total samples: {sample_count}")
    print(f"Trajectory points: {len(trajectory)}")
    print(f"Final position: ({state['position']['x']:.4f}, {state['position']['y']:.4f})")
    print(f"Max velocity: {state['max_velocity']:.4f} m/s")
    print(f"Total distance: {state['total_distance']:.4f} m")
    
    # Verify we got reasonable results
    if len(trajectory) > 50:
        print("✓ Sufficient trajectory points generated")
    else:
        print("✗ Insufficient trajectory points")
        return False
    
    if state['max_velocity'] > 0:
        print("✓ Movement detected")
    else:
        print("✗ No movement detected")
        return False
        
    if state['total_distance'] > 0:
        print("✓ Distance tracked")
    else:
        print("✗ No distance traveled")
        return False
    
    return True

def test_data_export():
    """Test data export functionality."""
    print("\nTesting data export...")
    
    simulator = IMUSimulator(sample_rate=10.0)
    tracker = MovementTracker()
    simulator.set_mode('random', speed=2.0)
    
    # Generate some data
    for i in range(30):
        imu_data = simulator.generate_sample()
        tracker.process_imu_sample(imu_data)
        time.sleep(0.01)
    
    # Test export
    export_data = tracker.export_trajectory_data()
    
    if len(export_data) > 20:
        print(f"✓ Export data contains {len(export_data)} points")
    else:
        print("✗ Export data too small")
        return False
        
    # Check data structure
    sample_point = export_data[0]
    required_fields = ['timestamp', 'x', 'y', 'vx', 'vy', 'velocity_magnitude']
    missing_fields = [field for field in required_fields if field not in sample_point]
    
    if missing_fields:
        print(f"✗ Export data missing fields: {missing_fields}")
        return False
    else:
        print("✓ Export data structure correct")
        
    return True

def main():
    """Run headless tests."""
    print("=" * 60)
    print("Dermograph Tracker - Headless Simulation Test")
    print("=" * 60)
    
    tests = [
        test_headless_simulation,
        test_data_export
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
            
    print("\n" + "=" * 60)
    print(f"Headless Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✓ All headless tests passed! Core functionality works correctly.")
        print("  The GUI application should run without issues.")
        return True
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)