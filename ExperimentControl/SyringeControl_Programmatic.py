#%% Fast Syringe Control with Strategic Logging (Programmatic Version)

from datetime import datetime
import serial
import time
import csv
import os

filename = 'E:/Harsh/Harsh/Nov25/today/control_programmatic_data.csv'

# Configure the serial connection
ser = serial.Serial(
    port='COM7',
    baudrate=115200,
    timeout=1
)

def send_command(command):
    """Send command and get response - keep this fast"""
    ser.write((command + '\r\n').encode())
    
    response = ""
    while True:
        line = ser.readline().decode().strip()
        if line:
            response += line + "\n"
        else:
            break
    
    print(f"Response for '{command}':")
    print(response)
    return response

def extract_volume_from_response(response):
    """Extract volume value from pump response"""
    lines = response.split('\n')
    for line in lines:
        if 'A:' in line:
            try:
                return float(line.split(' ')[1])
            except (ValueError, IndexError):
                return None
    return None

def initialize_csv_file():
    """Initialize CSV file with headers"""
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'timestamp', 
            'operation_type',  # 'infuse' or 'withdraw'
            'event_type',      # 'start', 'end', 'checkpoint'
            'target_volume_ul', 
            'current_volume_ul', 
            'speed_ul_per_min',
            'elapsed_time_s',
            'expected_time_s'  # theoretical time based on speed
        ])

def log_event(operation_type, event_type, target_volume, current_volume, speed, start_time):
    """Log a single event efficiently"""
    timestamp = datetime.now()
    elapsed_time = (timestamp - start_time).total_seconds() if start_time else 0
    expected_time = (target_volume / speed) * 60 if speed > 0 else 0
    
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            operation_type,
            event_type,
            target_volume,
            f"{current_volume:.3f}" if current_volume is not None else "0.000",
            speed,
            f"{elapsed_time:.3f}",
            f"{expected_time:.3f}"
        ])

def infuse_with_strategic_logging(volume, speed):
    """Fast infuse with strategic logging points"""
    print(f"Starting infusion: {volume} ul at {speed} ul/min")
    start_time = datetime.now()
    
    # Setup (fast)
    send_command(f'irate a {speed} ul/min')
    send_command('cvolume a')
    send_command(f'tvolume a {volume} ul')
    
    # Log start event
    log_event('infuse', 'start', volume, 0, speed, start_time)
    
    # Start operation
    send_command('irun a')
    print(f'Infusion started at {start_time.strftime("%H:%M:%S.%f")[:-3]}')
    
    # Calculate expected duration and set up checkpoints
    expected_duration = (volume / speed) * 60  # seconds
    
    # Strategic checkpoint (optional - only if operation is long)
    if expected_duration > 10:  # Only for operations longer than 10 seconds
        time.sleep(expected_duration * 0.5)  # Wait for halfway point
        response = send_command('ivolume a')
        current_vol = extract_volume_from_response(response)
        log_event('infuse', 'checkpoint', volume, current_vol, speed, start_time)
        print(f"Checkpoint: {current_vol} ul at 50% expected time")
    
    # Wait for completion with minimal checking
    time.sleep(max(0, expected_duration - (expected_duration * 0.5 if expected_duration > 10 else 0)))
    
    # Final check and log end
    response = send_command('ivolume a')
    final_volume = extract_volume_from_response(response)
    log_event('infuse', 'end', volume, final_volume, speed, start_time)
    
    end_time = datetime.now()
    actual_duration = (end_time - start_time).total_seconds()
    print(f"Infusion completed: {final_volume} ul in {actual_duration:.2f}s (expected: {expected_duration:.2f}s)")
    
    return final_volume, actual_duration

def withdraw_with_strategic_logging(volume, speed):
    """Fast withdraw with strategic logging points"""
    print(f"Starting withdrawal: {volume} ul at {speed} ul/min")
    start_time = datetime.now()
    
    # Setup (fast)
    send_command(f'wrate a {speed} ul/min')
    send_command('cvolume a')
    send_command(f'tvolume a {volume} ul')
    
    # Log start event
    log_event('withdraw', 'start', volume, 0, speed, start_time)
    
    # Start operation
    send_command('wrun a')
    print(f'Withdrawal started at {start_time.strftime("%H:%M:%S.%f")[:-3]}')
    
    # Calculate expected duration
    expected_duration = (volume / speed) * 60  # seconds
    
    # Strategic checkpoint (optional)
    if expected_duration > 10:
        time.sleep(expected_duration * 0.5)
        response = send_command('wvolume a')
        current_vol = extract_volume_from_response(response)
        log_event('withdraw', 'checkpoint', volume, current_vol, speed, start_time)
        print(f"Checkpoint: {current_vol} ul at 50% expected time")
    
    # Wait for completion
    time.sleep(max(0, expected_duration - (expected_duration * 0.5 if expected_duration > 10 else 0)))
    
    # Final check and log end
    response = send_command('wvolume a')
    final_volume = extract_volume_from_response(response)
    log_event('withdraw', 'end', volume, final_volume, speed, start_time)
    
    end_time = datetime.now()
    actual_duration = (end_time - start_time).total_seconds()
    print(f"Withdrawal completed: {final_volume} ul in {actual_duration:.2f}s (expected: {expected_duration:.2f}s)")
    
    return final_volume, actual_duration

#%% Initialize system
send_command('VER')
send_command('echo on')
time.sleep(1)
send_command('rsave off')

# Initialize CSV file
initialize_csv_file()

#%% Your experimental protocol - FAST execution
tWait = 30
disp1 = 1
speed1 = 20
NCycles=15
print('=== Starting Fast Protocol ===')
protocol_start = datetime.now()


print('\nWITHDRAWAL PHASE')
for i in range(1,NCycles+1 ):
    print(f'\n--- Withdrawal {i} ---')
    withdraw_with_strategic_logging(disp1, speed1)
    if i < NCycles:
        print(f"Waiting {tWait}s before next withdrawal...")
        time.sleep(tWait)
       #%%
# print('INFUSION PHASE')
# for i in range(1, NCycles+1):
#     print(f'\n--- Infusion {i} ---')
#     infuse_with_strategic_logging(disp1, speed1)
#     if i < NCycles:
#         print(f"Waiting {tWait}s before next infusion...")
#         time.sleep(tWait)

# protocol_end = datetime.now()
# total_time = (protocol_end - protocol_start).total_seconds()
# print(f'\n=== Protocol Complete in {total_time:.1f}s ===')

#%% Data Analysis and Plotting Functions

def load_strategic_data(csv_file=filename):
    """Load and process the strategic logging data"""
    import pandas as pd
    
    try:
        df = pd.read_csv(csv_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"Loaded {len(df)} strategic log events")
        print("Event breakdown:")
        print(df.groupby(['operation_type', 'event_type']).size())
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def create_interpolated_data(df):
    """Create smooth interpolated data for plotting from strategic points"""
    import pandas as pd
    import numpy as np
    
    interpolated_data = []
    
    # Group by operation instance
    operation_groups = df.groupby(['operation_type', 'target_volume_ul', 'speed_ul_per_min'])
    
    for (op_type, target_vol, speed), group in operation_groups:
        group = group.sort_values('elapsed_time_s')
        
        for i in range(len(group)):
            if group.iloc[i]['event_type'] == 'start':
                # Find corresponding end event
                start_row = group.iloc[i]
                end_idx = i + 1
                
                # Look for checkpoint and end
                checkpoint_row = None
                end_row = None
                
                for j in range(i + 1, len(group)):
                    if group.iloc[j]['event_type'] == 'checkpoint':
                        checkpoint_row = group.iloc[j]
                    elif group.iloc[j]['event_type'] == 'end':
                        end_row = group.iloc[j]
                        break
                
                if end_row is not None:
                    # Create interpolated timeline
                    start_time = start_row['elapsed_time_s']
                    end_time = end_row['elapsed_time_s']
                    duration = end_time - start_time
                    
                    # Create time points (every 0.1 seconds)
                    time_points = np.arange(start_time, end_time + 0.1, 0.1)
                    
                    # Linear interpolation for volume
                    start_vol = start_row['current_volume_ul']
                    end_vol = end_row['current_volume_ul']
                    
                    if checkpoint_row is not None:
                        # Use checkpoint for better interpolation
                        checkpoint_time = checkpoint_row['elapsed_time_s'] 
                        checkpoint_vol = checkpoint_row['current_volume_ul']
                        
                        # Piecewise linear interpolation
                        volumes = []
                        for t in time_points:
                            if t <= checkpoint_time:
                                # Interpolate between start and checkpoint
                                ratio = (t - start_time) / (checkpoint_time - start_time)
                                vol = start_vol + ratio * (checkpoint_vol - start_vol)
                            else:
                                # Interpolate between checkpoint and end
                                ratio = (t - checkpoint_time) / (end_time - checkpoint_time)
                                vol = checkpoint_vol + ratio * (end_vol - checkpoint_vol)
                            volumes.append(vol)
                    else:
                        # Simple linear interpolation
                        volumes = np.interp(time_points, [start_time, end_time], [start_vol, end_vol])
                    
                    # Add to interpolated data
                    for t, v in zip(time_points, volumes):
                        interpolated_data.append({
                            'timestamp': start_row['timestamp'] + pd.Timedelta(seconds=t-start_time),
                            'operation_type': op_type,
                            'target_volume_ul': target_vol,
                            'current_volume_ul': v,
                            'speed_ul_per_min': speed,
                            'elapsed_time_s': t,
                            'data_type': 'interpolated'
                        })
    
    return pd.DataFrame(interpolated_data)

def plot_syringe_data_strategic():
    """Create plots from strategic logging data"""
    import matplotlib.pyplot as plt
    import pandas as pd
    
    # Load strategic data
    df_strategic = load_strategic_data()
    if df_strategic is None:
        return
    
    # Create interpolated data for smooth plotting
    df_interpolated = create_interpolated_data(df_strategic)
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Strategic points only
    for op_type in df_strategic['operation_type'].unique():
        op_data = df_strategic[df_strategic['operation_type'] == op_type]
        axes[0,0].scatter(op_data['elapsed_time_s'], op_data['current_volume_ul'], 
                         label=f'{op_type} (strategic points)', alpha=0.7, s=50)
    
    axes[0,0].set_xlabel('Elapsed Time (s)')
    axes[0,0].set_ylabel('Volume (μl)')
    axes[0,0].set_title('Strategic Logging Points')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # Plot 2: Interpolated smooth data
    for op_type in df_interpolated['operation_type'].unique():
        op_data = df_interpolated[df_interpolated['operation_type'] == op_type]
        axes[0,1].plot(op_data['elapsed_time_s'], op_data['current_volume_ul'], 
                      label=f'{op_type} (interpolated)', linewidth=2)
    
    axes[0,1].set_xlabel('Elapsed Time (s)')
    axes[0,1].set_ylabel('Volume (μl)')
    axes[0,1].set_title('Interpolated Smooth Data')
    axes[0,1].legend()
    axes[0,1].grid(True)
    
    # Plot 3: Actual vs Expected timing
    operations = df_strategic[df_strategic['event_type'] == 'end']
    axes[1,0].scatter(operations['expected_time_s'], operations['elapsed_time_s'], 
                     c=['red' if op == 'infuse' else 'blue' for op in operations['operation_type']], 
                     alpha=0.7, s=60)
    
    # Perfect timing line
    max_time = max(operations['expected_time_s'].max(), operations['elapsed_time_s'].max())
    axes[1,0].plot([0, max_time], [0, max_time], 'k--', alpha=0.5, label='Perfect timing')
    
    axes[1,0].set_xlabel('Expected Time (s)')
    axes[1,0].set_ylabel('Actual Time (s)')
    axes[1,0].set_title('Timing Accuracy')
    axes[1,0].legend()
    axes[1,0].grid(True)
    
    # Plot 4: Operation summary
    summary_data = operations.groupby('operation_type').agg({
        'elapsed_time_s': ['mean', 'std'],
        'current_volume_ul': ['mean', 'std']
    }).round(3)
    
    axes[1,1].axis('off')
    axes[1,1].text(0.1, 0.9, 'Operation Summary:', fontsize=14, fontweight='bold', 
                   transform=axes[1,1].transAxes)
    
    y_pos = 0.7
    for op_type in summary_data.index:
        time_mean = summary_data.loc[op_type, ('elapsed_time_s', 'mean')]
        time_std = summary_data.loc[op_type, ('elapsed_time_s', 'std')]
        vol_mean = summary_data.loc[op_type, ('current_volume_ul', 'mean')]
        vol_std = summary_data.loc[op_type, ('current_volume_ul', 'std')]
        
        text = f"{op_type.capitalize()}:\n  Time: {time_mean:.2f}±{time_std:.2f}s\n  Volume: {vol_mean:.2f}±{vol_std:.2f}μl"
        axes[1,1].text(0.1, y_pos, text, fontsize=10, transform=axes[1,1].transAxes)
        y_pos -= 0.3
    
    plt.tight_layout()
    plt.show()
    
    return df_strategic, df_interpolated

# To run the analysis after your experiment:
df_strategic, df_interpolated = plot_syringe_data_strategic()