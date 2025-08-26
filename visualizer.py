"""
Visualization Engine for Dermograph Tracking Application.
Handles real-time plotting and data visualization using matplotlib.
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import List, Tuple, Optional, Dict
from collections import deque
import math


class DermographVisualizer:
    """Real-time visualizer for dermograph movement tracking."""
    
    def __init__(self, parent_frame=None, figure_size=(12, 8)):
        """
        Initialize the visualizer.
        
        Args:
            parent_frame: Parent tkinter frame (if embedding in GUI)
            figure_size: Size of the matplotlib figure
        """
        self.parent_frame = parent_frame
        self.figure_size = figure_size
        
        # Create matplotlib figure and subplots
        self.fig = plt.figure(figsize=figure_size, facecolor='white')
        self.fig.suptitle('Dermograph Movement Tracker', fontsize=14, fontweight='bold')
        
        # Create subplot layout
        self._setup_subplots()
        
        # Data storage for real-time plotting
        self.trajectory_x = deque(maxlen=2000)
        self.trajectory_y = deque(maxlen=2000)
        self.velocity_data = deque(maxlen=2000)
        self.accel_data = {'x': deque(maxlen=500), 'y': deque(maxlen=500), 'z': deque(maxlen=500)}
        self.angular_data = {'x': deque(maxlen=500), 'y': deque(maxlen=500), 'z': deque(maxlen=500)}
        self.time_data = deque(maxlen=500)
        
        # Visualization settings
        self.show_trail = True
        self.trail_length = 1000
        self.color_by_velocity = True
        self.show_orientation = True
        self.auto_scale = True
        
        # Current state for display
        self.current_position = {'x': 0.0, 'y': 0.0}
        self.current_velocity = 0.0
        self.current_orientation = 0.0
        self.max_velocity = 0.01  # Avoid division by zero
        self.total_distance = 0.0
        
        # Animation
        self.animation = None
        self.is_animating = False
        
        # Canvas for tkinter embedding
        self.canvas = None
        if parent_frame is not None:
            self.canvas = FigureCanvasTkAgg(self.fig, parent_frame)
            
    def _setup_subplots(self):
        """Setup the subplot layout."""
        # Main trajectory plot (larger, left side)
        self.ax_trajectory = self.fig.add_subplot(2, 3, (1, 4))
        self.ax_trajectory.set_title('2D Trajectory')
        self.ax_trajectory.set_xlabel('X Position (m)')
        self.ax_trajectory.set_ylabel('Y Position (m)')
        self.ax_trajectory.grid(True, alpha=0.3)
        self.ax_trajectory.set_aspect('equal')
        
        # Velocity plot
        self.ax_velocity = self.fig.add_subplot(2, 3, 2)
        self.ax_velocity.set_title('Velocity Magnitude')
        self.ax_velocity.set_xlabel('Time (s)')
        self.ax_velocity.set_ylabel('Velocity (m/s)')
        self.ax_velocity.grid(True, alpha=0.3)
        
        # Acceleration plots
        self.ax_accel = self.fig.add_subplot(2, 3, 3)
        self.ax_accel.set_title('Acceleration')
        self.ax_accel.set_xlabel('Time (s)')
        self.ax_accel.set_ylabel('Acceleration (m/s²)')
        self.ax_accel.grid(True, alpha=0.3)
        
        # Angular velocity plot
        self.ax_angular = self.fig.add_subplot(2, 3, 5)
        self.ax_angular.set_title('Angular Velocity')
        self.ax_angular.set_xlabel('Time (s)')
        self.ax_angular.set_ylabel('Angular Vel (rad/s)')
        self.ax_angular.grid(True, alpha=0.3)
        
        # Status/info panel
        self.ax_info = self.fig.add_subplot(2, 3, 6)
        self.ax_info.set_title('Current Status')
        self.ax_info.axis('off')
        
        # Initialize empty plots
        self.trajectory_line, = self.ax_trajectory.plot([], [], 'b-', alpha=0.7, linewidth=1)
        self.current_pos_marker, = self.ax_trajectory.plot([], [], 'ro', markersize=8)
        self.orientation_arrow = None
        
        self.velocity_line, = self.ax_velocity.plot([], [], 'g-', linewidth=2)
        
        self.accel_lines = {}
        colors = {'x': 'red', 'y': 'green', 'z': 'blue'}
        for axis, color in colors.items():
            line, = self.ax_accel.plot([], [], color=color, label=f'{axis.upper()}-axis', linewidth=1.5)
            self.accel_lines[axis] = line
        self.ax_accel.legend()
        
        self.angular_lines = {}
        for axis, color in colors.items():
            line, = self.ax_angular.plot([], [], color=color, label=f'{axis.upper()}-axis', linewidth=1.5)
            self.angular_lines[axis] = line
        self.ax_angular.legend()
        
        plt.tight_layout()
        
    def update_data(self, trajectory_point: Dict):
        """
        Update visualization with new trajectory point.
        
        Args:
            trajectory_point: New trajectory data point
        """
        # Extract data
        pos = trajectory_point['position']
        vel = trajectory_point['velocity']
        accel = trajectory_point['acceleration']
        angular_vel = trajectory_point['angular_velocity']
        timestamp = trajectory_point['timestamp']
        vel_magnitude = trajectory_point['velocity_magnitude']
        
        # Update current state
        self.current_position = pos
        self.current_velocity = vel_magnitude
        self.current_orientation = trajectory_point['orientation']['yaw']
        self.total_distance = trajectory_point.get('total_distance', 0.0)
        
        # Update max velocity for scaling
        if vel_magnitude > self.max_velocity:
            self.max_velocity = vel_magnitude
            
        # Store data for plotting
        self.trajectory_x.append(pos['x'])
        self.trajectory_y.append(pos['y'])
        self.velocity_data.append(vel_magnitude)
        
        self.accel_data['x'].append(accel['x'])
        self.accel_data['y'].append(accel['y'])
        self.accel_data['z'].append(accel['z'])
        
        self.angular_data['x'].append(angular_vel['x'])
        self.angular_data['y'].append(angular_vel['y'])
        self.angular_data['z'].append(angular_vel['z'])
        
        self.time_data.append(timestamp)
        
    def update_plots(self):
        """Update all plots with current data."""
        if not self.trajectory_x or not self.time_data:
            return
            
        # Update trajectory plot
        if self.show_trail:
            # Show full trail with color coding if enabled
            if self.color_by_velocity and len(self.velocity_data) > 1:
                # Create a scatter plot with velocity-based colors
                x_data = list(self.trajectory_x)
                y_data = list(self.trajectory_y)
                vel_data = list(self.velocity_data)
                
                # Clear previous scatter plot
                self.ax_trajectory.clear()
                self.ax_trajectory.set_title('2D Trajectory')
                self.ax_trajectory.set_xlabel('X Position (m)')
                self.ax_trajectory.set_ylabel('Y Position (m)')
                self.ax_trajectory.grid(True, alpha=0.3)
                self.ax_trajectory.set_aspect('equal')
                
                if len(x_data) > 1:
                    # Create velocity-colored trail
                    points = np.array([x_data, y_data]).T.reshape(-1, 1, 2)
                    segments = np.concatenate([points[:-1], points[1:]], axis=1)
                    
                    from matplotlib.collections import LineCollection
                    lc = LineCollection(segments, cmap='viridis', alpha=0.8)
                    lc.set_array(np.array(vel_data[:-1]))
                    lc.set_linewidth(2)
                    line = self.ax_trajectory.add_collection(lc)
                    
                    # Add colorbar if not present
                    if not hasattr(self, 'colorbar'):
                        self.colorbar = plt.colorbar(line, ax=self.ax_trajectory)
                        self.colorbar.set_label('Velocity (m/s)', rotation=270, labelpad=15)
            else:
                self.trajectory_line.set_data(list(self.trajectory_x), list(self.trajectory_y))
        else:
            # Show only recent points
            recent_x = list(self.trajectory_x)[-50:]
            recent_y = list(self.trajectory_y)[-50:]
            self.trajectory_line.set_data(recent_x, recent_y)
            
        # Update current position marker
        if self.trajectory_x and self.trajectory_y:
            self.current_pos_marker.set_data([self.trajectory_x[-1]], [self.trajectory_y[-1]])
            
            # Update orientation arrow
            if self.show_orientation:
                if self.orientation_arrow is not None:
                    self.orientation_arrow.remove()
                
                arrow_length = 0.05
                dx = arrow_length * math.cos(math.radians(self.current_orientation))
                dy = arrow_length * math.sin(math.radians(self.current_orientation))
                
                self.orientation_arrow = self.ax_trajectory.arrow(
                    self.trajectory_x[-1], self.trajectory_y[-1],
                    dx, dy, head_width=0.02, head_length=0.01, fc='red', ec='red'
                )
        
        # Auto-scale trajectory plot if enabled
        if self.auto_scale and self.trajectory_x and self.trajectory_y:
            x_data = list(self.trajectory_x)
            y_data = list(self.trajectory_y)
            if x_data and y_data:
                margin = 0.1
                x_range = max(x_data) - min(x_data)
                y_range = max(y_data) - min(y_data)
                
                if x_range > 0 and y_range > 0:
                    self.ax_trajectory.set_xlim(
                        min(x_data) - margin * x_range,
                        max(x_data) + margin * x_range
                    )
                    self.ax_trajectory.set_ylim(
                        min(y_data) - margin * y_range,
                        max(y_data) + margin * y_range
                    )
        
        # Update velocity plot
        if self.time_data and self.velocity_data:
            time_data = list(self.time_data)
            vel_data = list(self.velocity_data)
            
            # Convert to relative time
            if time_data:
                start_time = time_data[0]
                rel_time = [t - start_time for t in time_data]
                self.velocity_line.set_data(rel_time, vel_data)
                
                # Auto-scale
                if len(rel_time) > 1:
                    self.ax_velocity.set_xlim(0, max(rel_time))
                    if max(vel_data) > 0:
                        self.ax_velocity.set_ylim(0, max(vel_data) * 1.1)
        
        # Update acceleration plots
        if self.time_data:
            time_data = list(self.time_data)
            start_time = time_data[0] if time_data else 0
            rel_time = [t - start_time for t in time_data]
            
            for axis in ['x', 'y', 'z']:
                if self.accel_data[axis]:
                    accel_data = list(self.accel_data[axis])
                    self.accel_lines[axis].set_data(rel_time[-len(accel_data):], accel_data)
            
            # Auto-scale acceleration plot
            if rel_time:
                self.ax_accel.set_xlim(max(0, max(rel_time) - 10), max(rel_time))
                
                # Find y-axis limits
                all_accel = []
                for axis in ['x', 'y', 'z']:
                    all_accel.extend(list(self.accel_data[axis])[-100:])  # Recent data only
                
                if all_accel:
                    y_max = max(abs(min(all_accel)), abs(max(all_accel)))
                    self.ax_accel.set_ylim(-y_max * 1.1, y_max * 1.1)
        
        # Update angular velocity plots
        if self.time_data:
            for axis in ['x', 'y', 'z']:
                if self.angular_data[axis]:
                    angular_data = list(self.angular_data[axis])
                    self.angular_lines[axis].set_data(rel_time[-len(angular_data):], angular_data)
            
            # Auto-scale angular velocity plot
            if rel_time:
                self.ax_angular.set_xlim(max(0, max(rel_time) - 10), max(rel_time))
                
                # Find y-axis limits
                all_angular = []
                for axis in ['x', 'y', 'z']:
                    all_angular.extend(list(self.angular_data[axis])[-100:])
                
                if all_angular:
                    y_max = max(abs(min(all_angular)), abs(max(all_angular)))
                    self.ax_angular.set_ylim(-y_max * 1.1, y_max * 1.1)
        
        # Update info panel
        self._update_info_panel()
        
    def _update_info_panel(self):
        """Update the information display panel."""
        self.ax_info.clear()
        self.ax_info.axis('off')
        
        info_text = [
            f"Current Position:",
            f"  X: {self.current_position['x']:.3f} m",
            f"  Y: {self.current_position['y']:.3f} m",
            f"",
            f"Current Velocity: {self.current_velocity:.3f} m/s",
            f"Max Velocity: {self.max_velocity:.3f} m/s",
            f"",
            f"Orientation: {self.current_orientation:.1f}°",
            f"Total Distance: {self.total_distance:.3f} m",
            f"",
            f"Trail Points: {len(self.trajectory_x)}",
        ]
        
        text = '\n'.join(info_text)
        self.ax_info.text(0.05, 0.95, text, transform=self.ax_info.transAxes,
                         fontsize=10, verticalalignment='top', fontfamily='monospace')
        
    def clear_data(self):
        """Clear all visualization data."""
        self.trajectory_x.clear()
        self.trajectory_y.clear()
        self.velocity_data.clear()
        
        for axis in ['x', 'y', 'z']:
            self.accel_data[axis].clear()
            self.angular_data[axis].clear()
            
        self.time_data.clear()
        
        # Reset state
        self.current_position = {'x': 0.0, 'y': 0.0}
        self.current_velocity = 0.0
        self.current_orientation = 0.0
        self.max_velocity = 0.01
        self.total_distance = 0.0
        
        # Clear plots
        for line in [self.trajectory_line, self.current_pos_marker, self.velocity_line]:
            line.set_data([], [])
            
        for lines_dict in [self.accel_lines, self.angular_lines]:
            for line in lines_dict.values():
                line.set_data([], [])
                
        if self.orientation_arrow is not None:
            self.orientation_arrow.remove()
            self.orientation_arrow = None
            
        # Clear colorbar if it exists
        if hasattr(self, 'colorbar'):
            self.colorbar.remove()
            delattr(self, 'colorbar')
            
    def refresh_display(self):
        """Refresh the display."""
        self.update_plots()
        if self.canvas:
            self.canvas.draw()
        else:
            self.fig.canvas.draw()
            plt.pause(0.001)
            
    def get_canvas(self):
        """Get the matplotlib canvas for embedding in tkinter."""
        return self.canvas
        
    def save_plot(self, filename: str):
        """
        Save current plot to file.
        
        Args:
            filename: Output filename
        """
        try:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            return True
        except Exception as e:
            print(f"Error saving plot: {e}")
            return False
            
    def set_visualization_options(self, show_trail: bool = None, trail_length: int = None,
                                color_by_velocity: bool = None, show_orientation: bool = None,
                                auto_scale: bool = None):
        """
        Update visualization options.
        
        Args:
            show_trail: Whether to show trajectory trail
            trail_length: Maximum number of trail points
            color_by_velocity: Whether to color trail by velocity
            show_orientation: Whether to show orientation arrow
            auto_scale: Whether to auto-scale plots
        """
        if show_trail is not None:
            self.show_trail = show_trail
        if trail_length is not None:
            self.trail_length = trail_length
            # Update deque max lengths
            self.trajectory_x = deque(self.trajectory_x, maxlen=trail_length)
            self.trajectory_y = deque(self.trajectory_y, maxlen=trail_length)
        if color_by_velocity is not None:
            self.color_by_velocity = color_by_velocity
        if show_orientation is not None:
            self.show_orientation = show_orientation
        if auto_scale is not None:
            self.auto_scale = auto_scale