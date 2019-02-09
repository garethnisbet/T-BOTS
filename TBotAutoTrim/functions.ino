// functions for T-Bot

void vel(double h, double th){
	      dh=h-(h*cos(th*pi/180));
        if (th > 0){
	      vxy=sqrt(2*g*dh);
        }
        else{
          vxy=-sqrt(2*g*dh);
        }
        
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
  //tempRaw = (i2cData[6] << 8) | i2cData[7];
  //gyroX = (i2cData[8] << 8) | i2cData[9];
  gyroY = (i2cData[10] << 8) | i2cData[11];
  //gyroZ = (i2cData[12] << 8) | i2cData[13];

  
  float dt = (double)(micros() - timer) / 1000000; // Calculate delta time
  timer = micros();
 // pitch = atan2(-accZ, sqrt(accY * accY + accX * accX)) * RAD_TO_DEG;
  double pitch = atan2(-accZ, -accX) * RAD_TO_DEG;
  gyroYrate = gyroY / 131.0; // Convert to deg/s
  
  CFilteredlAngleY = CFilterY.getAngle(pitch, gyroYrate, dt); // Calculate the angle using a Simple Combination filter
  CFilterY.setWeighting(filter_weighting);
 // gyroYangle += gyroYrate * dt; // Calculate gyro angle without any filter
  
  /*
  Serial.print(dt); Serial.print("\t");
  Serial.print(pitch); Serial.print("\t");
  Serial.print(gyroYrate); Serial.print("\t");
  Serial.print(CFilteredlAngleY); Serial.print("\t");
  Serial.print(gyroYangle); Serial.print("\t");
  Serial.print("\n");
  */

} // end of gyro function

void getJoystickState(byte databt[8])    {
  joyX = (databt[1]-48)*100 + (databt[2]-48)*10 + (databt[3]-48);       // obtain the Int from the ASCII representation
  joyY = (databt[4]-48)*100 + (databt[5]-48)*10 + (databt[6]-48);
  joyXdiff = joyX - joyXbefore;
  joyYdiff = joyY - joyYbefore;
  if (abs(joyXdiff) <= 100){
  joyXf = joyX - 200;// Offset to avoid transmitting negative numbers
  }
  if (abs(joyYdiff) <= 100){
  joyYf = joyY - 200;
  }
  joyXbefore = joyX;
  joyYbefore = joyY;
  /*
  Serial.print(joyX); Serial.print("\t");
  Serial.print(joyY); Serial.print("\t");
  Serial.print("\n");
  */
  
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
      KP += 0.02;
      break;
    case 'F':
      buttonStatus &= B111011;      
      KP += 0.02;
      break;

// -----------------  BUTTON #4  -----------------------
    case 'G':
      buttonStatus |= B001000;      
      KP -= 0.02;
    break;
    case 'H':
      buttonStatus &= B110111;    
      KP -= 0.02;
    break;

// -----------------  BUTTON #5  -----------------------
    case 'I':           // configured as momentary button
      gtrim += 0.05;
      break;
   case 'J':
     buttonStatus &= B101111;        // OFF
      gtrim += 0.05;    
     break;

// -----------------  BUTTON #6  -----------------------
    case 'K':
      buttonStatus |= B100000;        // ON
      gtrim -= 0.05;
     break;
    case 'L':
      gtrim -= 0.05;
      break;
// -----------------  BUTTON #7  -----------------------
    case 'T':
      buttonStatus |= B100000;        // ON
      autotrim = 1;
     break;

}
}


