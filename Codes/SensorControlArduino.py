import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)
    
#%%

import serial
import time

# Set up the serial connection (port may vary on different computers)
ser = serial.Serial('/dev/cu.usbmodem14101', 9600, timeout=1)
time.sleep(2)  # Wait for the connection to settle

# Open a file to write the data
with open('analog_data.txt', 'w') as file:
    file.write("Raw Value, Voltage\n")  # Write header
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(line)  # Print to console
                file.write(line + '\n')  # Write to file
                file.flush()  # Ensure data is written to file
    except KeyboardInterrupt:
        print("Data collection stopped by user")
    finally:
        ser.close()  # Close the serial connection


##################################Arduino code       
# void setup() {
#   Serial.begin(9600);  // Initialize serial communication at 9600 bps
# }

# void loop() {
#   // Read the analog value from pin A0
#   int sensorValue = analogRead(analogPin);
  
#   // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
#   float voltage = sensorValue * (5.0 / 1023.0);
  
#   // Print the results to Serial in a comma-separated format
#   Serial.print(sensorValue);
#   Serial.print(",");
#   Serial.println(voltage);
  
#   // Wait for a moment before the next reading
#   delay(1000);  // Delay for 1 second (1000 milliseconds)
# }
#
#
#
#
