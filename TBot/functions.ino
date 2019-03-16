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

void refreshTuningFields(int bStatus)  {
        switch (bStatus){
        case 'A':
         
            KPS -= 0.01;
            
          break;
        
        case 'B':

            KPS += 0.01;

            
          break;
        
        case 'C':
           
            KP -= 0.1;

           
          break;
        
        case 'D':
            
            KP += 0.1;

                    
          break;
                  
        case 'E':
            
            gtrim -= 0.1;

          
          break;
        
        case 'F':
            
            gtrim += 0.1;
           
          break;
        
        case 'T':
            autotrim = 1;
            break;

        case 'Z':
            StopII = 0;
        break;   
        }

        array1[7]= 'Z';
        incflag = 0; 
        
}
        
void setJoystick(byte databt[8]){
   joyXcheck = (databt[1]-48)*100 + (databt[2]-48)*10 + (databt[3]-48);       // obtain the Int from the ASCII representation
   joyYcheck = (databt[4]-48)*100 + (databt[5]-48)*10 + (databt[6]-48);
    if (joyXcheck < 300 && joyYcheck < 300){
      joyX = joyXcheck - 200;
      joyY = joyYcheck - 200;
      
    }
  joyXdiff = joyX - joyXbefore;
  joyYdiff = joyY - joyYbefore;
  if (abs(joyXdiff) <= 300){
  joyXf = joyX;// Offset to avoid transmitting negative numbers
  }
  if (abs(joyYdiff) <= 100){
  joyYf = joyY;
  }
  joyXbefore = joyX;
  joyYbefore = joyY;
  
}
