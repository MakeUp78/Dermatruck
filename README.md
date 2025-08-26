# Dermograph Movement Tracker

A Python application for simulating and visualizing dermograph movements based on IMU sensor data. This application provides real-time 2D visualization of dermograph trajectories with comprehensive data analysis and export capabilities.

## Features

### Core Functionality
- **Real-time IMU Data Simulation**: Generates realistic sensor data mimicking a Witmotion IMU sensor
- **2D Movement Visualization**: Live trajectory plotting with velocity-based color coding
- **Multiple Operation Modes**: Demo patterns, random movements, and trajectory replay
- **Interactive Dashboard**: Real-time display of position, velocity, acceleration, and orientation
- **Data Export/Import**: Save and load trajectories in CSV and JSON formats

### Visualization Capabilities
- **Trajectory Plotting**: 2D path visualization with customizable trail length
- **Velocity Color Mapping**: Visual representation of movement intensity
- **Orientation Display**: Direction arrows showing dermograph orientation
- **Real-time Graphs**: Live plots of acceleration, angular velocity, and velocity magnitude
- **Auto-scaling**: Automatic plot scaling for optimal viewing

### Interactive Controls
- **Start/Stop/Reset**: Full simulation control
- **Speed Adjustment**: Variable simulation speed (0.1x to 5.0x)
- **Visualization Options**: Toggle trail display, color coding, orientation arrows
- **Data Management**: Save plots as images, export trajectory data

## Installation

### Prerequisites
- Python 3.8 or higher
- Required Python packages (see requirements.txt)

### Setup
1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
```bash
python main.py
```

## Usage

### Getting Started
1. **Launch the application** by running `python main.py`
2. **Select a simulation mode**:
   - **Demo**: Predefined patterns simulating dermograph techniques
   - **Random**: Smooth random movements with realistic characteristics
   - **Replay**: Load and replay previously saved trajectories
3. **Adjust simulation speed** using the speed slider
4. **Click "Start Simulation"** to begin tracking
5. **Monitor real-time data** in the visualization panels and statistics display

### Simulation Modes

#### Demo Mode
Predefined movement patterns that simulate common dermographic techniques:
- **Straight Lines**: Linear movements with controlled acceleration
- **Circular Motions**: Smooth circular patterns
- **Figure-8 Patterns**: Complex curved trajectories
- **Stippling**: Rapid on/off movements simulating dotting techniques

#### Random Mode
Generates smooth, realistic random movements using:
- Multi-frequency sinusoidal components for natural motion
- Variable pressure simulation through Z-axis acceleration
- Controlled angular velocity changes for realistic orientation

#### Replay Mode
Load and visualize previously saved trajectory data:
- Compatible with exported JSON files
- Full trajectory reconstruction with timing information
- Maintains original movement characteristics

### Data Export Options

#### CSV Export
- Timestamp, position coordinates, velocity components
- Acceleration values for all axes
- Orientation angles (roll, pitch, yaw)
- Cumulative distance and velocity magnitude

#### JSON Export
- Complete trajectory data with full precision
- Hierarchical data structure for easy parsing
- Compatible with replay mode for visualization

#### Plot Export
- High-resolution images (PNG, PDF, SVG formats)
- Publication-ready figures with all current display settings
- Preserves color coding and annotations

### Visualization Controls

#### Trail Display Options
- **Show Trail**: Toggle trajectory path visibility
- **Trail Length**: Adjust number of displayed points (100-3000)
- **Color by Velocity**: Enable velocity-based color mapping
- **Auto Scale**: Automatic plot range adjustment

#### Real-time Graphs
- **Acceleration**: X, Y, Z components over time
- **Angular Velocity**: Roll, pitch, yaw rates
- **Velocity Magnitude**: Overall movement speed
- **Position Statistics**: Current coordinates and total distance

## Technical Details

### Data Format
The application uses a standardized IMU data format compatible with ROS:

```python
{
    'timestamp': float,                                    # Unix timestamp
    'linear_acceleration': {'x': float, 'y': float, 'z': float},  # m/s²
    'angular_velocity': {'x': float, 'y': float, 'z': float},     # rad/s
    'orientation': {'x': float, 'y': float, 'z': float, 'w': float},  # Quaternion
    'magnetic_field': {'x': float, 'y': float, 'z': float}       # µT
}
```

### Movement Tracking Algorithm
1. **Noise Filtering**: Low-pass filtering to reduce sensor noise
2. **Gravity Compensation**: Removes gravitational acceleration component
3. **Integration**: Double integration from acceleration to position
4. **Drift Compensation**: Periodic velocity decay to reduce accumulated errors
5. **2D Projection**: Converts 3D movement to 2D trajectory for visualization

### Performance Optimization
- **Threading**: Separate simulation and GUI threads for smooth operation
- **Data Limiting**: Configurable trajectory length to manage memory usage
- **Efficient Rendering**: Optimized matplotlib updates for real-time display
- **Adaptive Scaling**: Dynamic plot range adjustment for optimal viewing

## File Structure

```
Dermatruck/
├── main.py                 # Application entry point
├── gui.py                  # Main GUI interface
├── imu_simulator.py        # IMU data generation
├── movement_tracker.py     # Movement calculation and tracking
├── visualizer.py          # Real-time visualization engine
├── utils.py               # Utility functions and data handling
├── requirements.txt       # Python dependencies
└── README.md             # This documentation
```

## Extending the Application

### Adding New Movement Patterns
1. Extend the `_generate_demo_movement()` method in `imu_simulator.py`
2. Add pattern selection logic based on time progression
3. Include realistic acceleration and angular velocity profiles

### Custom Data Sources
1. Modify `IMUSimulator` class to accept external data feeds
2. Implement data format conversion if necessary
3. Maintain timing synchronization for real-time visualization

### Advanced Filtering
1. Extend `MovementTracker` with additional filter types
2. Implement Kalman filtering for improved accuracy
3. Add sensor fusion capabilities for multiple data sources

## Troubleshooting

### Common Issues
- **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
- **Performance Issues**: Reduce trail length or simulation speed for better performance
- **Display Problems**: Check that your system supports matplotlib with tkinter backend

### Platform-Specific Notes
- **Linux**: May require `python3-tk` package for tkinter support
- **macOS**: Use Python installed via Homebrew for best compatibility
- **Windows**: Ensure Python is properly added to system PATH

## Future Enhancements

### Planned Features
- **Real Sensor Integration**: Connect to actual Witmotion IMU via ROS driver
- **3D Visualization**: Full three-dimensional trajectory display
- **Pattern Recognition**: Automatic detection of common dermograph techniques
- **Advanced Analytics**: Statistical analysis of movement patterns
- **Multi-session Comparison**: Compare trajectories across different sessions

### Extensibility
The application is designed with modular architecture to support:
- Additional sensor types and data formats
- Custom visualization modes and display options
- Advanced filtering and processing algorithms
- Integration with external analysis tools

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Contact

For questions, issues, or suggestions, please create an issue in the repository.