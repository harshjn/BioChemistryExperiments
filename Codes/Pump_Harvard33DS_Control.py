import serial
import time

# Configure the serial connection
ser = serial.Serial(
    port='COM7',
    baudrate=115200,  # Adjust this to match your device's baud rate
    timeout=1
)

# Command to send
command = 'VER\r\n'  # '\r\n' is often used as line ending, adjust if needed

# Send the command
ser.write(command.encode())

# Read the response
response = ""
while True:
    line = ser.readline().decode().strip()
    if line:
        response += line + "\n"
    else:
        # No more data received, assume response is complete
        break

# Print the response
print("Response received:")
print(response)

# Close the serial connection
ser.close()
