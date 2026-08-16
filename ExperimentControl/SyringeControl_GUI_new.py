# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 12:03:32 2025

@author: Leica-Admin
"""
               
from datetime import datetime
import serial
import time
import tkinter as tk
from tkinter import ttk
import threading
import os

#%% Configuration
filename = 'E:/Harsh/Harsh/2026/today/control_GUI_data1.txt'
voltage_filename = 'E:/Harsh/Harsh/2026/today/DisplayVoltsData.txt'

# Configure the serial connection
ser = serial.Serial(
    port='COM7',
    baudrate=115200,
    timeout=1
)

#%% Serial Communication Functions
def send_command(command):
    """Send command and get response - optimized for speed"""
    ser.write((command + '\r\n').encode())
    
    response = ""
    while True:
        line = ser.readline().decode().strip()
        if line:
            response += line + "\n"
        else:
            break
    return response

def extract_volume_from_response(response):
    """Quick volume extraction"""
    lines = response.split('\n')
    for line in lines:
        if 'A:' in line:
            try:
                return float(line.split(' ')[1])
            except (ValueError, IndexError):
                return 0.0
    return 0.0

#%% Initialize Serial Communication
send_command('VER')
send_command('echo on')
time.sleep(1)
send_command('rsave off')

# Initialize data file with headers if it doesn't exist
if not os.path.exists(filename) or os.path.getsize(filename) == 0:
    with open(filename, 'w') as file:
        file.write("# Syringe Control Data Log\n")
        file.write("# Timestamp, Operation, Speed (ul/min), Volume (ul)\n")

# Operation tracking
operation_in_progress = False
operation_history = []

#%% Syringe Operation Class
class FastSyringeOperation:
    """Fast, non-blocking syringe operation with enhanced logging"""
    
    def __init__(self, operation_type, volume, speed):
        self.operation_type = operation_type
        self.volume = volume
        self.speed = speed
        self.is_running = False
        self.expected_time = (volume / speed) * 60  # seconds
        self.start_time = None
        
    def start(self):
        """Start operation in background thread"""
        global operation_in_progress
        
        if operation_in_progress:
            return False
            
        operation_in_progress = True
        self.is_running = True
        self.start_time = datetime.now()
        
        # Update GUI immediately
        status_var.set(f"{self.operation_type.capitalize()}ing...")
        progress_var.set(f"0.0 / {self.volume} μl")
        progress_bar["maximum"] = self.volume
        progress_bar["value"] = 0
        
        # Update status label color
        status_label.configure(foreground='#0066cc')
        
        # Start operation in background
        thread = threading.Thread(target=self._run_operation, daemon=True)
        thread.start()
        
        return True
    
    def _run_operation(self):
        """Run the actual operation"""
        try:
            # Fast setup - no intermediate checks
            if self.operation_type == 'infuse':
                send_command(f'irate a {self.speed} ul/min')
                send_command('cvolume a')
                send_command(f'tvolume a {self.volume} ul')
                send_command('irun a')
            else:  # withdraw
                send_command(f'wrate a {self.speed} ul/min')
                send_command('cvolume a')
                send_command(f'tvolume a {self.volume} ul')
                send_command('wrun a')
            
            # Start progress monitoring
            window.after(100, self._check_progress)
            
        except Exception as e:
            print(f"Operation error: {e}")
            self._complete_operation(0)
    
    def _check_progress(self):
        """Check progress - called from main thread"""
        if not self.is_running:
            return
        
        try:
            # Get current volume
            if self.operation_type == 'infuse':
                response = send_command('ivolume a')
            else:
                response = send_command('wvolume a')
            
            current_vol = extract_volume_from_response(response)
            
            # Save timestamped data with speed
            self._save_data(current_vol)
            
            # Calculate elapsed and remaining time
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if current_vol > 0:
                estimated_total = (self.volume / current_vol) * elapsed
                remaining = max(0, estimated_total - elapsed)
            else:
                remaining = self.expected_time
            
            # Update GUI
            progress_var.set(f"{current_vol:.1f} / {self.volume} μl")
            time_var.set(f"Elapsed: {elapsed:.1f}s | Remaining: ~{remaining:.1f}s")
            progress_bar["value"] = current_vol
            
            # Check completion (with tolerance)
            if abs(current_vol - self.volume) < 0.5:
                self._complete_operation(current_vol)
            else:
                # Schedule next check - adaptive timing
                check_interval = 500 if current_vol < self.volume * 0.1 else 200
                window.after(check_interval, self._check_progress)
                
        except Exception as e:
            print(f"Progress check error: {e}")
            window.after(1000, self._check_progress)  # Retry after error
    
    def _save_data(self, current_volume):
        """Save timestamped volume data with speed"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            operation_label = self.operation_type.capitalize()
            
            with open(filename, 'a') as file:
                file.write(f"{timestamp}, {operation_label}, {self.speed}, {current_volume:.3f}\n")
                file.flush()
            
            print(f"{timestamp}, {operation_label}, {self.speed} μl/min, {current_volume:.3f} μl")
            
        except Exception as e:
            print(f"Data save error: {e}")
    
    def _complete_operation(self, final_volume):
        """Complete the operation"""
        global operation_in_progress
        
        self.is_running = False
        operation_in_progress = False
        
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        # Update GUI
        status_var.set(f"{self.operation_type.capitalize()} Complete")
        progress_var.set(f"{final_volume:.1f} / {self.volume} μl (Done)")
        time_var.set(f"Total time: {elapsed_time:.1f}s")
        progress_bar["value"] = final_volume
        status_label.configure(foreground='#008800')
        
        # Add to operation history
        history_entry = f"{datetime.now().strftime('%H:%M:%S')} - {self.operation_type.capitalize()}: {final_volume:.1f} μl @ {self.speed} μl/min ({elapsed_time:.1f}s)"
        operation_history.append(history_entry)
        update_history_display()
        
        print(f"{self.operation_type.capitalize()} completed: {final_volume:.1f} μl in {elapsed_time:.1f}s")

#%% Operation Control Functions
def start_infuse():
    """Start infusion"""
    volume = volume_var.get()
    speed = speed_var.get()
    
    if volume <= 0 or speed <= 0:
        status_var.set("Invalid parameters!")
        status_label.configure(foreground='red')
        return
    
    operation = FastSyringeOperation('infuse', volume, speed)
    if not operation.start():
        status_var.set("Operation already running!")
        status_label.configure(foreground='orange')

def start_withdraw():
    """Start withdrawal"""
    volume = volume_var.get()
    speed = speed_var.get()
    
    if volume <= 0 or speed <= 0:
        status_var.set("Invalid parameters!")
        status_label.configure(foreground='red')
        return
    
    operation = FastSyringeOperation('withdraw', volume, speed)
    if not operation.start():
        status_var.set("Operation already running!")
        status_label.configure(foreground='orange')

def stop_operation():
    """Emergency stop"""
    global operation_in_progress
    try:
        send_command('stop a')
        operation_in_progress = False
        status_var.set("STOPPED")
        status_label.configure(foreground='red')
        progress_var.set("Operation stopped")
        time_var.set("")
    except Exception as e:
        print(f"Stop error: {e}")

#%% GUI Setup
# Create main window
window = tk.Tk()
window.title('Syringe Control System')
window.geometry("350x700")
window.configure(bg='#f5f5f5')

# Style configuration
style = ttk.Style()
style.theme_use('clam')

# Configure custom button styles
style.configure('Infuse.TButton', font=('Arial', 8, 'bold'), foreground='#0066cc')
style.configure('Withdraw.TButton', font=('Arial', 8, 'bold'), foreground='#cc6600')
style.configure('Stop.TButton', font=('Arial', 8, 'bold'), foreground='#cc0000')

# Title
title_label = tk.Label(window, text="Syringe Pump Control", 
                       font=('Arial', 8, 'bold'), bg='#f5f5f5', fg='#333333')
title_label.pack(pady=(1, 5))

# Main control frame
control_frame = ttk.LabelFrame(window, text="Operation Parameters", padding="20")
control_frame.pack(padx=10, pady=1, fill="x")

# Parameters frame with better spacing
params_frame = ttk.Frame(control_frame)
params_frame.pack(fill="x", pady=(0, 1))

# Speed input
speed_var = tk.IntVar(value=100)
ttk.Label(params_frame, text='Flow Rate (μl/min):', 
         font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 15), pady=8)
speed_entry = ttk.Entry(params_frame, textvariable=speed_var, width=15, font=('Arial', 11))
speed_entry.grid(row=0, column=1, sticky='w', pady=8)

# Volume input
volume_var = tk.IntVar(value=30)
ttk.Label(params_frame, text='Target Volume (μl):', 
         font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=(0, 15), pady=1)
volume_entry = ttk.Entry(params_frame, textvariable=volume_var, width=15, font=('Arial', 11))
volume_entry.grid(row=1, column=1, sticky='w', pady=1)

# Expected time display
expected_time_var = tk.StringVar(value="Expected duration: 18.0s")
expected_time_label = ttk.Label(params_frame, textvariable=expected_time_var, 
                               font=('Arial', 10), foreground='#666666')
expected_time_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=(5, 0))

def update_expected_time(*args):
    """Update expected time when parameters change"""
    try:
        vol = volume_var.get()
        spd = speed_var.get()
        if spd > 0:
            exp_time = (vol / spd) * 60
            expected_time_var.set(f"Expected duration: {exp_time:.1f}s")
        else:
            expected_time_var.set("Expected duration: --")
    except:
        expected_time_var.set("Expected duration: --")

# Bind parameter changes
volume_var.trace('w', update_expected_time)
speed_var.trace('w', update_expected_time)

# Operation buttons frame with better spacing
buttons_frame = ttk.Frame(control_frame)
buttons_frame.pack(fill="x", pady=(2, 0))

# Infuse button
infuse_btn = ttk.Button(buttons_frame, text="▶ INFUSE", command=start_infuse, 
                       style='Infuse.TButton')
infuse_btn.pack(side="left", padx=(0, 6), ipadx=8, ipady=1)

# Withdraw button
withdraw_btn = ttk.Button(buttons_frame, text="◀ WITHDRAW", command=start_withdraw,
                         style='Withdraw.TButton')
withdraw_btn.pack(side="left", padx=(0, 6), ipadx=8, ipady=1)

# Stop button
stop_btn = ttk.Button(buttons_frame, text="■ STOP", command=stop_operation,
                     style='Stop.TButton')
stop_btn.pack(side="right", ipadx=6, ipady=1)

# Status frame
status_frame = ttk.LabelFrame(window, text="Current Status", padding="6")
status_frame.pack(padx=6, pady=1, fill="x")

# Status display
status_var = tk.StringVar(value="Ready")
status_label = tk.Label(status_frame, textvariable=status_var, 
                       font=('Arial', 8, 'bold'), fg='#008800', bg='white', 
                       relief='sunken', padx=10, pady=5)
status_label.pack(fill='x', pady=(0, 1))

# Progress display
progress_var = tk.StringVar(value="0.0 / 0.0 μl")
progress_label = ttk.Label(status_frame, textvariable=progress_var, font=('Arial', 11))
progress_label.pack(anchor="w", pady=(0, 5))

# Time display
time_var = tk.StringVar(value="")
time_label = ttk.Label(status_frame, textvariable=time_var, font=('Arial', 10), 
                      foreground='#666666')
time_label.pack(anchor="w", pady=(0, 1))
# Voltage monitoring frame
voltage_frame = ttk.LabelFrame(window, text="System Monitoring", padding="15")
voltage_frame.pack(padx=20, pady=(0, 1), fill="x")

# Voltage displays
mean_voltage_var = tk.StringVar(value="Mean Voltage: Loading...")
std_voltage_var = tk.StringVar(value="Std Dev: Loading...")

voltage_info_frame = ttk.Frame(voltage_frame)
voltage_info_frame.pack(fill="x")

ttk.Label(voltage_info_frame, textvariable=mean_voltage_var, 
         font=('Arial', 10)).pack(side="left", padx=(0, 20))
ttk.Label(voltage_info_frame, textvariable=std_voltage_var, 
         font=('Arial', 10)).pack(side="left")


# Progress bar

progress_bar = ttk.Progressbar(status_frame, length=420, mode="determinate")
progress_bar.pack(pady=(0, 1))

# Operation History Frame
history_frame = ttk.LabelFrame(window, text="Operation History (Last 5)", padding="15")
history_frame.pack(padx=20, pady=15, fill="both", expand=True)

# History text widget
history_text = tk.Text(history_frame, height=6, width=55, font=('Courier', 9),
                      bg='#fafafa', relief='sunken', borderwidth=1)
history_text.pack(fill='both', expand=True)
history_text.config(state='disabled')

def update_history_display():
    """Update the operation history display"""
    history_text.config(state='normal')
    history_text.delete(1.0, tk.END)
    
    # Show last 5 operations
    recent_ops = operation_history[-5:]
    for entry in recent_ops:
        history_text.insert(tk.END, entry + '\n')
    
    history_text.config(state='disabled')



# Voltage-based suggestions
voltage_suggestion_var = tk.StringVar(value="Status: Monitoring...")
suggestion_label = ttk.Label(voltage_frame, textvariable=voltage_suggestion_var, 
                            font=('Arial', 9, 'italic'))
suggestion_label.pack(pady=(1, 0))

def load_voltage_data():
    """Load voltage data and provide suggestions"""
    try:
        with open(voltage_filename, 'r') as file:
            lines = file.readlines()
            mean_voltage = float(lines[0].strip())
            std_voltage = float(lines[1].strip())

            # Update displays
            mean_voltage_var.set(f"Mean Voltage: {mean_voltage:.4f}V")
            std_voltage_var.set(f"Std Dev: {std_voltage:.4f}V")
            
            # Voltage-based suggestions with color coding
            if std_voltage > 0.01:  # High noise
                suggestion = "Status: High noise detected - consider reducing flow rate"
                suggestion_label.configure(foreground='#cc0000')
            elif mean_voltage > 4.5:  # High voltage
                suggestion = "Status: Optimal conditions for operation"
                suggestion_label.configure(foreground='#008800')
            elif mean_voltage < 1.0:  # Low voltage
                suggestion = "Status: Low voltage - use moderate speeds"
                suggestion_label.configure(foreground='#cc6600')
            else:
                suggestion = "Status: Normal operating conditions"
                suggestion_label.configure(foreground='#0066cc')
            
            voltage_suggestion_var.set(suggestion)

    except (IndexError, ValueError, FileNotFoundError) as e:
        mean_voltage_var.set("Mean Voltage: Error")
        std_voltage_var.set("Std Dev: Error")
        voltage_suggestion_var.set("Status: Voltage data unavailable")
        suggestion_label.configure(foreground='#999999')

    # Update every 2 seconds
    window.after(2000, load_voltage_data)

#%% Cleanup Function
def on_closing():
    """Clean shutdown"""
    try:
        if operation_in_progress:
            send_command('stop a')
        ser.close()
    except:
        pass
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

#%% Start Application
# Start voltage monitoring
load_voltage_data()

# Initial expected time calculation
update_expected_time()

print("=" * 50)
print("Syringe Control System Initialized")
print("=" * 50)
print(f"Data logging to: {filename}")
print("Ready for operation...")
print("=" * 50)

# Start the GUI
window.mainloop()