"""
GUI Interface for Dermograph Tracking Application.
Main application window with controls and visualization.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from typing import Optional, Dict
import json

from imu_simulator import IMUSimulator
from movement_tracker import MovementTracker
from visualizer import DermographVisualizer
from utils import save_trajectory_csv, save_trajectory_json, load_trajectory_json


class DermographGUI:
    """Main GUI application for dermograph tracking."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("Dermograph Movement Tracker")
        self.root.geometry("1400x900")
        
        # Application state
        self.is_running = False
        self.simulation_thread = None
        self.current_mode = 'demo'
        self.simulation_speed = 1.0
        self.update_rate = 50  # ms
        
        # Core components
        self.imu_simulator = IMUSimulator(sample_rate=50.0)  # 50 Hz
        self.movement_tracker = MovementTracker(filter_alpha=0.1)
        
        # GUI components
        self.setup_gui()
        
        # Initialize visualizer
        self.visualizer = DermographVisualizer(
            parent_frame=self.plot_frame,
            figure_size=(10, 8)
        )
        
        # Pack the canvas
        canvas = self.visualizer.get_canvas()
        if canvas:
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        # Start GUI update loop
        self.update_display()
        
    def setup_gui(self):
        """Setup the main GUI layout."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel for visualization
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup control panels
        self.setup_control_panel(control_frame)
        
    def setup_control_panel(self, parent):
        """Setup the control panel with buttons and options."""
        # Control panel width
        control_width = 250
        
        # Title
        title_label = ttk.Label(parent, text="Dermograph Tracker", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Simulation controls
        sim_frame = ttk.LabelFrame(parent, text="Simulation Control", padding=10)
        sim_frame.pack(fill=tk.X, pady=(0, 10))
        sim_frame.configure(width=control_width)
        
        # Start/Stop button
        self.start_button = ttk.Button(sim_frame, text="Start Simulation", 
                                      command=self.toggle_simulation)
        self.start_button.pack(fill=tk.X, pady=(0, 5))
        
        # Reset button
        reset_button = ttk.Button(sim_frame, text="Reset", 
                                 command=self.reset_simulation)
        reset_button.pack(fill=tk.X, pady=(0, 5))
        
        # Mode selection
        mode_label = ttk.Label(sim_frame, text="Simulation Mode:")\n        mode_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.mode_var = tk.StringVar(value='demo')
        mode_frame = ttk.Frame(sim_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 5))
        
        modes = [('Demo', 'demo'), ('Random', 'random'), ('Replay', 'replay')]
        for i, (text, value) in enumerate(modes):
            radio = ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var,
                                   value=value, command=self.change_mode)
            radio.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0, 10))
        
        # Speed control
        speed_label = ttk.Label(sim_frame, text="Simulation Speed:")
        speed_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(sim_frame, from_=0.1, to=5.0, 
                               variable=self.speed_var, orient=tk.HORIZONTAL,
                               command=self.change_speed)
        speed_scale.pack(fill=tk.X, pady=(0, 5))
        
        self.speed_label = ttk.Label(sim_frame, text="1.0x")
        self.speed_label.pack(anchor=tk.W)
        
        # Visualization controls
        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding=10)
        viz_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Checkboxes for visualization options
        self.show_trail_var = tk.BooleanVar(value=True)
        trail_check = ttk.Checkbutton(viz_frame, text="Show Trail", 
                                     variable=self.show_trail_var,
                                     command=self.update_viz_options)
        trail_check.pack(anchor=tk.W, pady=2)
        
        self.color_velocity_var = tk.BooleanVar(value=True)
        color_check = ttk.Checkbutton(viz_frame, text="Color by Velocity", 
                                     variable=self.color_velocity_var,
                                     command=self.update_viz_options)
        color_check.pack(anchor=tk.W, pady=2)
        
        self.show_orientation_var = tk.BooleanVar(value=True)
        orient_check = ttk.Checkbutton(viz_frame, text="Show Orientation", 
                                      variable=self.show_orientation_var,
                                      command=self.update_viz_options)
        orient_check.pack(anchor=tk.W, pady=2)
        
        self.auto_scale_var = tk.BooleanVar(value=True)
        scale_check = ttk.Checkbutton(viz_frame, text="Auto Scale", 
                                     variable=self.auto_scale_var,
                                     command=self.update_viz_options)
        scale_check.pack(anchor=tk.W, pady=2)
        
        # Trail length
        trail_label = ttk.Label(viz_frame, text="Trail Length:")
        trail_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.trail_var = tk.IntVar(value=1000)
        trail_scale = ttk.Scale(viz_frame, from_=100, to=3000,
                               variable=self.trail_var, orient=tk.HORIZONTAL,
                               command=self.update_viz_options)
        trail_scale.pack(fill=tk.X)
        
        # Statistics display
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=8, width=30, font=('Courier', 9))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Data management
        data_frame = ttk.LabelFrame(parent, text="Data Management", padding=10)
        data_frame.pack(fill=tk.X, pady=(0, 10))
        
        save_csv_btn = ttk.Button(data_frame, text="Save CSV", 
                                 command=self.save_csv)
        save_csv_btn.pack(fill=tk.X, pady=(0, 2))
        
        save_json_btn = ttk.Button(data_frame, text="Save JSON", 
                                  command=self.save_json)
        save_json_btn.pack(fill=tk.X, pady=(0, 2))
        
        load_btn = ttk.Button(data_frame, text="Load Trajectory", 
                             command=self.load_trajectory)
        load_btn.pack(fill=tk.X, pady=(0, 2))
        
        save_plot_btn = ttk.Button(data_frame, text="Save Plot", 
                                  command=self.save_plot)
        save_plot_btn.pack(fill=tk.X, pady=(0, 2))
        
        # Clear button
        clear_btn = ttk.Button(data_frame, text="Clear Display", 
                              command=self.clear_display)
        clear_btn.pack(fill=tk.X, pady=(5, 0))
        
    def toggle_simulation(self):
        """Start or stop the simulation."""
        if self.is_running:
            self.stop_simulation()
        else:
            self.start_simulation()
            
    def start_simulation(self):
        """Start the simulation thread."""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="Stop Simulation")
            
            # Configure simulator
            self.imu_simulator.set_mode(self.current_mode, self.simulation_speed)
            
            # Start simulation thread
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            
    def stop_simulation(self):
        """Stop the simulation."""
        self.is_running = False
        self.start_button.config(text="Start Simulation")
        
    def reset_simulation(self):
        """Reset the simulation and clear data."""
        was_running = self.is_running
        if was_running:
            self.stop_simulation()
            
        # Reset components
        self.imu_simulator.reset()
        self.movement_tracker.reset()
        self.visualizer.clear_data()
        
        # Update display
        self.visualizer.refresh_display()
        self.update_stats_display()
        
    def simulation_loop(self):
        """Main simulation loop running in separate thread."""
        while self.is_running:
            try:
                # Generate IMU sample
                imu_data = self.imu_simulator.generate_sample()
                
                # Process through movement tracker
                trajectory_point = self.movement_tracker.process_imu_sample(imu_data)
                
                # Update visualizer
                self.visualizer.update_data(trajectory_point)
                
                # Sleep to maintain sample rate
                time.sleep(1.0 / self.imu_simulator.sample_rate)
                
            except Exception as e:
                print(f"Simulation error: {e}")
                break
                
        self.is_running = False
        
    def change_mode(self):
        """Handle mode change."""
        self.current_mode = self.mode_var.get()
        if hasattr(self, 'imu_simulator'):
            self.imu_simulator.set_mode(self.current_mode, self.simulation_speed)
            
    def change_speed(self, value=None):
        """Handle speed change."""
        self.simulation_speed = self.speed_var.get()
        self.speed_label.config(text=f"{self.simulation_speed:.1f}x")
        if hasattr(self, 'imu_simulator'):
            self.imu_simulator.set_mode(self.current_mode, self.simulation_speed)
            
    def update_viz_options(self, event=None):
        """Update visualization options."""
        if hasattr(self, 'visualizer'):
            self.visualizer.set_visualization_options(
                show_trail=self.show_trail_var.get(),
                trail_length=self.trail_var.get(),
                color_by_velocity=self.color_velocity_var.get(),
                show_orientation=self.show_orientation_var.get(),
                auto_scale=self.auto_scale_var.get()
            )
            
    def update_display(self):
        """Update the display in the main thread."""
        try:
            # Update visualization
            if hasattr(self, 'visualizer'):
                self.visualizer.refresh_display()
                
            # Update statistics
            self.update_stats_display()
            
        except Exception as e:
            print(f"Display update error: {e}")
            
        # Schedule next update
        self.root.after(self.update_rate, self.update_display)
        
    def update_stats_display(self):
        """Update the statistics text display."""
        if hasattr(self, 'movement_tracker'):
            state = self.movement_tracker.get_current_state()
            
            stats_text = f"""Current Status:
Position:
  X: {state['position']['x']:.3f} m
  Y: {state['position']['y']:.3f} m

Velocity:
  X: {state['velocity']['x']:.3f} m/s
  Y: {state['velocity']['y']:.3f} m/s
  Magnitude: {state['velocity_magnitude']:.3f} m/s

Acceleration:
  X: {state['acceleration']['x']:.3f} m/s²
  Y: {state['acceleration']['y']:.3f} m/s²
  Z: {state['acceleration']['z']:.3f} m/s²

Orientation:
  Roll: {state['orientation']['roll']:.1f}°
  Pitch: {state['orientation']['pitch']:.1f}°
  Yaw: {state['orientation']['yaw']:.1f}°

Statistics:
  Max Velocity: {state['max_velocity']:.3f} m/s
  Total Distance: {state['total_distance']:.3f} m
  Trail Points: {state['trajectory_length']}
  
Status: {'Running' if self.is_running else 'Stopped'}
Mode: {self.current_mode.title()}
Speed: {self.simulation_speed:.1f}x"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
    def save_csv(self):
        """Save trajectory data to CSV file."""
        if not hasattr(self, 'movement_tracker'):
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Trajectory as CSV"
        )
        
        if filename:
            data = self.movement_tracker.export_trajectory_data()
            if save_trajectory_csv(data, filename):
                messagebox.showinfo("Success", f"Trajectory saved to {filename}")
            else:
                messagebox.showerror("Error", "Failed to save CSV file")
                
    def save_json(self):
        """Save trajectory data to JSON file."""
        if not hasattr(self, 'movement_tracker'):
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Trajectory as JSON"
        )
        
        if filename:
            data = self.movement_tracker.export_trajectory_data()
            if save_trajectory_json(data, filename):
                messagebox.showinfo("Success", f"Trajectory saved to {filename}")
            else:
                messagebox.showerror("Error", "Failed to save JSON file")
                
    def load_trajectory(self):
        """Load trajectory data from JSON file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Load Trajectory from JSON"
        )
        
        if filename:
            data = load_trajectory_json(filename)
            if data:
                # Stop current simulation
                was_running = self.is_running
                if was_running:
                    self.stop_simulation()
                    
                # Clear current data
                self.visualizer.clear_data()
                self.movement_tracker.reset()
                
                # Load data into visualizer
                for point in data:
                    # Convert loaded data back to trajectory point format
                    trajectory_point = {
                        'timestamp': point['timestamp'],
                        'position': {'x': point['x'], 'y': point['y']},
                        'velocity': {'x': point['vx'], 'y': point['vy']},
                        'acceleration': {'x': point['ax'], 'y': point['ay'], 'z': point['az']},
                        'orientation': {'roll': point['roll'], 'pitch': point['pitch'], 'yaw': point['yaw']},
                        'angular_velocity': {'x': 0.0, 'y': 0.0, 'z': 0.0},  # Not saved in export
                        'velocity_magnitude': point['velocity_magnitude'],
                        'total_distance': point['total_distance']
                    }
                    self.visualizer.update_data(trajectory_point)
                    
                self.visualizer.refresh_display()
                messagebox.showinfo("Success", f"Loaded {len(data)} trajectory points")
            else:
                messagebox.showerror("Error", "Failed to load JSON file")
                
    def save_plot(self):
        """Save current plot to image file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")],
            title="Save Plot"
        )
        
        if filename:
            if hasattr(self, 'visualizer'):
                if self.visualizer.save_plot(filename):
                    messagebox.showinfo("Success", f"Plot saved to {filename}")
                else:
                    messagebox.showerror("Error", "Failed to save plot")
                    
    def clear_display(self):
        """Clear the display data."""
        if hasattr(self, 'visualizer'):
            self.visualizer.clear_data()
            self.visualizer.refresh_display()
        if hasattr(self, 'movement_tracker'):
            self.movement_tracker.reset()
            
    def run(self):
        """Run the GUI application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_simulation()
            self.root.destroy()
            
    def __del__(self):
        """Cleanup when application is destroyed."""
        if hasattr(self, 'is_running') and self.is_running:
            self.is_running = False