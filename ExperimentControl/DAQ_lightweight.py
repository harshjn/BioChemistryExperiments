# -*- coding: utf-8 -*-
"""
Real-time DAQ - Lightweight Data Acquisition
Created on Fri Nov 8 11:12:11 2024
@author: Leica-Admin

OPTIMIZED FOR SPEED - Plotting disabled by default
Main purpose: Fast, reliable data acquisition and logging
"""

#%% Imports
import nidaqmx
from nidaqmx.system import System
from nidaqmx.constants import TerminalConfiguration
from datetime import datetime, timedelta
import time
import numpy as np

#%% Configuration
filename = 'E:/Harsh/Harsh/2026/today/analog_data1.txt'
display_filename = 'E:/Harsh/Harsh/2026/today/DisplayVoltsData.txt'

device_name = 'Dev1'
channel_name = f"{device_name}/ai0"
samples_to_read = 1000  # Number of samples per acquisition
sample_rate = 10000     # Samples per second (10 kHz)

# Plotting control - SET TO False FOR MAXIMUM SPEED
enable_plotting = False  # Default: OFF (plotting now in Syringe GUI)

#%% Optional Plotting Setup (only if enabled)
if enable_plotting:
    import matplotlib.pyplot as plt
    from collections import deque
    import matplotlib.dates as mdates
    
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('Real-time Voltage Monitoring', fontsize=14, fontweight='bold')
    
    max_plot_points = 100
    time_data = deque(maxlen=max_plot_points)
    mean_data = deque(maxlen=max_plot_points)
    std_data = deque(maxlen=max_plot_points)
    
    def update_plot(time_list, mean_list, std_list):
        """Update the real-time plots (only if plotting enabled)"""
        if len(time_list) == 0:
            return
        
        ax1.clear()
        std_array = np.array(std_list)
        if std_array.max() > 0:
            sizes = 50 + (std_array / std_array.max()) * 450
        else:
            sizes = np.ones(len(std_list)) * 100
        
        ax1.scatter(time_list, mean_list, s=sizes, c='blue', alpha=0.6, 
                   edgecolors='navy', linewidth=0.5)
        ax1.plot(time_list, mean_list, 'b-', alpha=0.3, linewidth=1)
        ax1.set_xlabel('Time', fontsize=11)
        ax1.set_ylabel('Mean Voltage (V)', fontsize=11)
        ax1.set_title('Mean Voltage (Point size ∝ Std)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        if len(mean_list) > 0:
            mean_array = np.array(mean_list)
            y_min = mean_array.min() - 0.1
            y_max = mean_array.max() + 0.1
            ax1.set_ylim(y_min, y_max)
        
        ax2.clear()
        ax2.plot(time_list, std_list, 'r-', linewidth=2, label='Std Dev')
        ax2.fill_between(time_list, 0, std_list, alpha=0.3, color='red')
        ax2.set_xlabel('Time', fontsize=11)
        ax2.set_ylabel('Std Deviation (V)', fontsize=11)
        ax2.set_title('Voltage Standard Deviation', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax2.legend()
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        if len(std_list) > 0:
            y_max = std_array.max() * 1.2
            ax2.set_ylim(0, y_max)
        
        plt.tight_layout()
        plt.pause(0.01)

#%% Initialize System
system = System.local()

print("=" * 60)
print("Available NI-DAQmx devices:")
for device in system.devices:
    print(f"Device Name: {device.name}, Product Type: {device.product_type}")
print("=" * 60)

#%% Helper Functions
def save_display_data(mean_val, std_val):
    """Save mean and std to display file (for syringe control GUI)"""
    try:
        with open(display_filename, 'w') as file2:
            file2.write(f"{mean_val}\n{std_val}")
            file2.flush()
    except Exception as e:
        print(f"Error saving display data: {e}")

#%% Test Single Acquisition
print("\nTesting single acquisition...")
start_time = datetime.now()

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan(
        channel_name,
        terminal_config=TerminalConfiguration.RSE,
        min_val=-10.0,
        max_val=10.0
    )
    
    task.timing.cfg_samp_clk_timing(rate=sample_rate, 
                                   samps_per_chan=samples_to_read)
    timestart = time.time()
    
    values = task.read(number_of_samples_per_channel=samples_to_read)
    
    print(f"Acquisition time: {(time.time() - timestart):.4f} seconds")
    print(f"Samples read: {len(values)}")
    print(f"Mean voltage: {np.mean(values):.5f} V")
    print(f"Std deviation: {np.std(values):.5f} V")

print("\n" + "=" * 60)
print("Starting continuous data acquisition...")
if enable_plotting:
    print("Plotting: ENABLED")
else:
    print("Plotting: DISABLED (View in Syringe Control GUI)")
print("Press Ctrl+C to stop")
print("=" * 60 + "\n")

#%% Main Acquisition Loop
acquisition_count = 0

with open(filename, 'a') as file:
    try: 
        while True:
            start_time = datetime.now()
            timestart = time.time()
        
            # Acquire data
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(
                    channel_name,
                    terminal_config=TerminalConfiguration.RSE,
                    min_val=-10.0,
                    max_val=10.0
                )
            
                task.timing.cfg_samp_clk_timing(rate=sample_rate, 
                                           samps_per_chan=samples_to_read)
            
                # Read samples
                values = task.read(number_of_samples_per_channel=samples_to_read)
            
                # Calculate statistics
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                # Save to display file (for syringe GUI)
                save_display_data(mean_val, std_val)
                
                # Write all samples to file
                for i, voltage in enumerate(values):
                    sample_timestamp = start_time + timedelta(seconds=i * (1.0 / sample_rate))
                    data_line = f"{sample_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')}, {voltage:.5f}\n"
                    file.write(data_line)
                
                file.flush()
                
            # Update plot if enabled
            acquisition_count += 1
            if enable_plotting:
                time_data.append(start_time)
                mean_data.append(mean_val)
                std_data.append(std_val)
                update_plot(list(time_data), list(mean_data), list(std_data))
            
            # Console output
            elapsed = time.time() - timestart
            print(f"[{start_time.strftime('%H:%M:%S')}] "
                  f"Mean: {mean_val:.5f}V | Std: {std_val:.5f}V | "
                  f"Time: {elapsed:.3f}s | Count: {acquisition_count}", 
                  end='\n')

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Data collection stopped by user")
        print(f"Total acquisitions: {acquisition_count}")
        print(f"Total samples collected: {acquisition_count * samples_to_read}")
        print(f"Data saved to: {filename}")
        print("=" * 60)
        
    finally:
        if enable_plotting:
            plt.ioff()
            plt.show()
