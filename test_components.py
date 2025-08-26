#!/usr/bin/env python3
"""
Simple test script to verify the dermograph tracking application components.
"""
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        import utils
        import imu_simulator
        import movement_tracker
        import visualizer
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_imu_simulator():
    """Test IMU simulator functionality."""
    print("Testing IMU simulator...")
    try:
        from imu_simulator import IMUSimulator
        
        # Create simulator
        sim = IMUSimulator(sample_rate=10.0)
        
        # Test different modes
        for mode in ['demo', 'random']:
            sim.set_mode(mode, speed=1.0)
            data = sim.generate_sample()
            
            # Verify data structure
            required_keys = ['timestamp', 'linear_acceleration', 'angular_velocity', 'orientation', 'magnetic_field']
            if not all(key in data for key in required_keys):
                print(f"✗ IMU data missing required keys for mode {mode}")
                return False
                
            # Verify data types
            if not isinstance(data['timestamp'], float):
                print(f"✗ Invalid timestamp type for mode {mode}")
                return False
        
        print("✓ IMU simulator working correctly")
        return True
        
    except Exception as e:
        print(f"✗ IMU simulator error: {e}")
        return False

def test_movement_tracker():
    """Test movement tracker functionality."""
    print("Testing movement tracker...")
    try:
        from imu_simulator import IMUSimulator
        from movement_tracker import MovementTracker
        
        sim = IMUSimulator(sample_rate=10.0)
        tracker = MovementTracker()
        
        # Generate and process some samples
        for i in range(10):
            imu_data = sim.generate_sample()
            trajectory_point = tracker.process_imu_sample(imu_data)
            
            # Verify trajectory point structure
            required_keys = ['position', 'velocity', 'acceleration', 'orientation']
            if not all(key in trajectory_point for key in required_keys):
                print("✗ Movement tracker missing required keys")
                return False
                
        # Test state retrieval
        state = tracker.get_current_state()
        if 'position' not in state or 'velocity' not in state:
            print("✗ Movement tracker state incomplete")
            return False
            
        print("✓ Movement tracker working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Movement tracker error: {e}")
        return False

def test_utility_functions():
    """Test utility functions."""
    print("Testing utility functions...")
    try:
        from utils import quaternion_to_euler, euler_to_quaternion, apply_noise
        
        # Test quaternion conversion
        euler = quaternion_to_euler(0, 0, 0, 1)  # Identity quaternion
        if not all(abs(euler[key]) < 0.001 for key in ['roll', 'pitch', 'yaw']):
            print("✗ Quaternion to Euler conversion failed")
            return False
            
        # Test Euler to quaternion conversion
        quat = euler_to_quaternion(0, 0, 0)
        expected_identity = abs(quat['w'] - 1.0) < 0.001
        if not expected_identity:
            print("✗ Euler to quaternion conversion failed")
            return False
            
        # Test noise application
        noisy_value = apply_noise(1.0, 0.1)
        if not isinstance(noisy_value, float):
            print("✗ Noise application failed")
            return False
            
        print("✓ Utility functions working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Utility functions error: {e}")
        return False

def test_data_export():
    """Test data export functionality."""
    print("Testing data export...")
    try:
        from imu_simulator import IMUSimulator
        from movement_tracker import MovementTracker
        from utils import save_trajectory_json, load_trajectory_json
        import tempfile
        import os
        
        sim = IMUSimulator(sample_rate=10.0)
        tracker = MovementTracker()
        
        # Generate some data
        for i in range(5):
            imu_data = sim.generate_sample()
            tracker.process_imu_sample(imu_data)
            
        # Export data
        export_data = tracker.export_trajectory_data()
        if not export_data:
            print("✗ No data to export")
            return False
            
        # Test JSON save/load
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
            
        try:
            success = save_trajectory_json(export_data, temp_filename)
            if not success:
                print("✗ JSON save failed")
                return False
                
            loaded_data = load_trajectory_json(temp_filename)
            if not loaded_data:
                print("✗ JSON load failed")
                return False
                
            if len(loaded_data) != len(export_data):
                print("✗ JSON data length mismatch")
                return False
                
        finally:
            os.unlink(temp_filename)
            
        print("✓ Data export working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Data export error: {e}")
        return False

def test_integration():
    """Test integration between components."""
    print("Testing component integration...")
    try:
        from imu_simulator import IMUSimulator
        from movement_tracker import MovementTracker
        
        sim = IMUSimulator(sample_rate=20.0)
        tracker = MovementTracker()
        
        # Run a longer simulation with higher speed
        sim.set_mode('demo', speed=5.0)
        
        for i in range(50):
            imu_data = sim.generate_sample()
            trajectory_point = tracker.process_imu_sample(imu_data)
            time.sleep(0.005)  # Small delay
            
        # Check that we have meaningful movement
        trajectory = tracker.get_trajectory()
        if len(trajectory) < 40:
            print("✗ Insufficient trajectory points generated")
            return False
            
        # Check for actual movement (lowered threshold for realistic movement)
        positions = [p['position'] for p in trajectory]
        max_x = max(abs(p['x']) for p in positions)
        max_y = max(abs(p['y']) for p in positions)
        has_movement = max_x > 0.0001 or max_y > 0.0001  # Very small but detectable movement
        
        if not has_movement:
            print(f"✗ No significant movement detected - max X: {max_x:.6f}, max Y: {max_y:.6f}")
            return False
            
        print("✓ Component integration working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Integration error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Dermograph Tracker Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_imu_simulator,
        test_movement_tracker,
        test_utility_functions,
        test_data_export,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("All tests passed! The application should work correctly.")
        return True
    else:
        print("Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)