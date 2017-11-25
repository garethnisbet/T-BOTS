// functions for omnidrive

void velxy(double h, double th){
	      dh=h-(h*cos(th*pi/180));
	      vxy=sqrt(2*g*dh)*th/abs(th);
	     // vxy=v*cos(acos((h-dh)/h))*th/abs(th);
       // vxy = v*th/abs(th);
        //a2vnorm = sqrt((sin(th*pi/180.0)*sin(th*pi/180.0)) +(sin(phi*pi/180)*sin(phi*pi/180.0)));
}

void v2ang(double h, double v){
  if(v < 0){
        angout = -acos(1-((v*v)/(2*g*h)))*180/pi;
  }
  else{
    angout = acos(1-((v*v)/(2*g*h)))*180/pi;
  }
  if (angout != angout){
    angout = 0;
  }
}


void gyroread(){
  /* Update all the values */
  
  while (i2cRead(0x3B, i2cData, 14));
  accX = ((i2cData[0] << 8) | i2cData[1]);
  accY = ((i2cData[2] << 8) | i2cData[3]);
  accZ = ((i2cData[4] << 8) | i2cData[5]);
  tempRaw = (i2cData[6] << 8) | i2cData[7];
  gyroX = (i2cData[8] << 8) | i2cData[9];
  gyroY = (i2cData[10] << 8) | i2cData[11];
  gyroZ = (i2cData[12] << 8) | i2cData[13];

  double dt = (double)(micros() - timer) / 1000000; // Calculate delta time
  timer = micros();

#ifdef RESTRICT_PITCH // Eq. 25 and 26
  double roll  = atan2(accY, accZ) * RAD_TO_DEG;
  double pitch = atan(-accX / sqrt(accY * accY + accZ * accZ)) * RAD_TO_DEG;
#else // Eq. 28 and 29
  double roll  = atan(accY / sqrt(accX * accX + accZ * accZ)) * RAD_TO_DEG;
  double pitch = atan2(-accX, accZ) * RAD_TO_DEG;
#endif

  double gyroXrate = gyroX / 131.0; // Convert to deg/s
  double gyroYrate = gyroY / 131.0; // Convert to deg/s

#ifdef RESTRICT_PITCH
  // This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
  if ((roll < -90 && kalAngleX > 90) || (roll > 90 && kalAngleX < -90)) {
    kalmanX.setAngle(roll);
    compAngleX = roll;
    kalAngleX = roll;
    gyroXangle = roll;
  } else
    kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter

  if (abs(kalAngleX) > 90)
    gyroYrate = -gyroYrate; // Invert rate, so it fits the restriced accelerometer reading
  kalAngleY = kalmanY.getAngle(pitch, gyroYrate, dt);
#else
  // This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
  if ((pitch < -90 && kalAngleY > 90) || (pitch > 90 && kalAngleY < -90)) {
    kalmanY.setAngle(pitch);
    compAngleY = pitch;
    kalAngleY = pitch;
    gyroYangle = pitch;
  } else
    kalAngleY = kalmanY.getAngle(pitch, gyroYrate, dt); // Calculate the angle using a Kalman filter

  if (abs(kalAngleY) > 90)
    gyroXrate = -gyroXrate; // Invert rate, so it fits the restriced accelerometer reading
  kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter
#endif

  gyroXangle += gyroXrate * dt; // Calculate gyro angle without any filter
  gyroYangle += gyroYrate * dt;
  //gyroXangle += kalmanX.getRate() * dt; // Calculate gyro angle using the unbiased rate
  //gyroYangle += kalmanY.getRate() * dt;

  compAngleX = 0.93 * (compAngleX + gyroXrate * dt) + 0.07 * roll; // Calculate the angle using a Complimentary filter
  compAngleY = 0.93 * (compAngleY + gyroYrate * dt) + 0.07 * pitch;

  // Reset the gyro angle when it has drifted too much
  if (gyroXangle < -180 || gyroXangle > 180)
    gyroXangle = kalAngleX;
  if (gyroYangle < -180 || gyroYangle > 180)
    gyroYangle = kalAngleY;

} // end of gyro function

/*
void gyroreadnofilter()
{
  // Read normalized values 
  Vector normAccel = mpu.readNormalizeAccel();

  // Calculate Pitch & Roll
  pitch = -(atan2(normAccel.XAxis, sqrt(normAccel.YAxis*normAccel.YAxis + normAccel.ZAxis*normAccel.ZAxis))*180.0)/M_PI;
  roll = (atan2(normAccel.YAxis, normAccel.ZAxis)*180.0)/M_PI;


}
*/

void getJoystickState(byte databt[8])    {
  joyX = (databt[1]-48)*100 + (databt[2]-48)*10 + (databt[3]-48);       // obtain the Int from the ASCII representation
  joyY = (databt[4]-48)*100 + (databt[5]-48)*10 + (databt[6]-48);
  joyXdiff = joyX - joyXbefore;
  joyYdiff = joyY - joyYbefore;
  if (abs(joyXdiff) <= 100){
  joyXf = joyX - 200;// Offset to avoid
  }
  if (abs(joyYdiff) <= 100){
  joyYf = joyY - 200;// transmitting negative numbers
  }
  joyXbefore = joyX;
  joyYbefore = joyY;
}



void getButtonState(int bStatus)  {
  switch (bStatus) {
// -----------------  BUTTON #1  -----------------------
    case 'A':
      buttonStatus |= B000001;    
      KPS += 0.01;
      break;
    case 'B':
      buttonStatus &= B111110;      
      KPS += 0.01;

      break;

// -----------------  BUTTON #2  -----------------------
    case 'C':
      buttonStatus |= B000010;    
      KPS -= 0.01;
      break;
    case 'D':
      buttonStatus &= B111101;    
      KPS -= 0.01;
      break;

// -----------------  BUTTON #3  -----------------------
    case 'E':
      buttonStatus |= B000100;        
      KP += 0.1;
      break;
    case 'F':
      buttonStatus &= B111011;      
      KP += 0.1;
      break;

// -----------------  BUTTON #4  -----------------------
    case 'G':
      buttonStatus |= B001000;      
      KP -= 0.1;
    break;
    case 'H':
      buttonStatus &= B110111;    
      KP -= 0.1;
    break;

// -----------------  BUTTON #5  -----------------------
    case 'I':           // configured as momentary button
      gtrim += 0.02;
      break;
   case 'J':
     buttonStatus &= B101111;        // OFF
      gtrim += 0.02;    
     break;

// -----------------  BUTTON #6  -----------------------
    case 'K':
      buttonStatus |= B100000;        // ON
      gtrim -= 0.02;
     break;
    case 'L':
      gtrim -= 0.02;
      break;

}
}


