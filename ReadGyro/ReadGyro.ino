#include <Wire.h>

double pitch, gyroYrate, accX, accY, accZ,  gyroX, gyroY, gyroZ, tempRaw;
uint8_t i2cData[14]; // Buffer for I2C data
uint32_t timer;
void setup(){

  TWBR = ((F_CPU / 400000L) - 16) / 2; // Set I2C frequency to 400kHz
  i2cData[0] = 7; // Set the sample rate to 1000Hz - 8kHz/(7+1) = 1000Hz
  i2cData[1] = 0x00; // Disable FSYNC and set 260 Hz Acc filtering, 256 Hz Gyro filtering, 8 KHz sampling
  i2cData[2] = 0x00; // Set Gyro Full Scale Range to ±250deg/s
  i2cData[3] = 0x00; // Set Accelerometer Full Scale Range to ±2g
  while (i2cWrite(0x19, i2cData, 4, false)); // Write to all four registers at once
  while (i2cWrite(0x6B, 0x01, true)); // PLL with X axis gyroscope reference and disable sleep mode 
  while (i2cRead(0x75, i2cData, 1));
  if (i2cData[0] != 0x68) { // Read "WHO_AM_I" register
    Serial.print(F("Error reading sensor"));
    while (1);
  }
  delay(100); // Wait for sensor to stabilize

 
Serial.begin(38400);
}

void loop(){

  while (i2cRead(0x3B, i2cData, 14));
   accX = ((i2cData[0] << 8) | i2cData[1]);
   accY = ((i2cData[2] << 8) | i2cData[3]);
   accZ = ((i2cData[4] << 8) | i2cData[5]);
   tempRaw = (i2cData[6] << 8) | i2cData[7];
   gyroX = (i2cData[8] << 8) | i2cData[9];
   gyroY = (i2cData[10] << 8) | i2cData[11];
   gyroZ = (i2cData[12] << 8) | i2cData[13];

  
   float dt = (double)(micros() - timer) / 1000000; // Calculate delta time
   timer = micros();
   // pitch = atan2(-accZ, sqrt(accY * accY + accX * accX)) * RAD_TO_DEG;
   double pitch = atan2(-accZ, -accX) * RAD_TO_DEG;
   gyroYrate = gyroY / 131.0; // Convert to deg/s

  
   Serial.print(pitch); Serial.print('\t');
   Serial.print(gyroYrate); Serial.print('\t');

   Serial.print('\n');
   
}
