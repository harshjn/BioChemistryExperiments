const int analogPin = A0;  // Analog input pin

void setup() {
  Serial.begin(9600);  // Initialize serial communication at 9600 bps
}

void loop() {
  // Read the analog value from pin A0
  int sensorValue = analogRead(analogPin);
  
  // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  float voltage = sensorValue * (5.0 / 1023.0);
  
  // Print the results to Serial in a comma-separated format
  Serial.print(sensorValue);
  Serial.print(",");
  Serial.println(voltage);
  
  // Wait for a moment before the next reading
  delay(100);  // Delay for 1 second (1000 milliseconds)
}
