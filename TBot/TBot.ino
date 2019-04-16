
//////////////////   Import libraries here    ///////////////////
#include <TaskScheduler.h>
#include <Motor.h>
#include <PID_v1.h>
#include <Filters.h>
#include <NewPing.h>
#include <SoftwareSerial.h>
#include <RunningAverage.h> // Running average filter
#include <Wire.h>
#include "Combination_Filter.h" 

///////////////  Setup preprocessor directives ///////////////////
#define    STX          0x02
#define    ETX          0x03
#define    comma        0x2C

////////////     Setup variables  //////////////////////////////// 
byte data[9] = {STX, 50, 48, 48, 50, 48, 48, ETX};
byte letter;
byte array1[10] = {STX, 50, 48, 48, 50, 48, 48, 90, ETX};
int joyXdiff, joyYdiff,joyXcheck, joyYcheck, joyXbefore, joyYbefore, joyX, joyY, boflag;
float joyXf, joyYf; 
float backoff;
int ii, iii;
String Data = "";
int StopII, autotrim;
float g = 9.81, pi = 3.1416, h = 0.08; // physical constants
float dh, th, phi, v, vxy, vx, vy, vz, norm, vxs, vys, angout;
float accX, accY, accZ;
int incflag;
char character;
///////   Tuning ////////////////////////////////////////////

//float gtrim = 4.3, rtrim = 0;
float gtrim = 6.3, rtrim = 0;


float controller_sensitivity = 1.5, spinval, spinfactor = 0.8;
float speedpidsampletime = 2;
float gyropidsampletime = 2;
float filter_weighting = 0.015;
float speedKp=0.10;
float speedKi=0;
double speedKd=0.00, KPS = 0.10, KP = 4.20, KI = 65, KPS_last, KP_last, KI_last;
String sendKPS, sendKP, sendgtrim;
double gyroKp=4.2, gyroKi=65, gyroKd=0.0;

//double speedKd=0.00, KPS = 0.02, KP = 2.00, KI = 55, KPS_last, KP_last, KI_last;
//String sendKPS, sendKP, sendgtrim;
//double gyroKp=2.0, gyroKi=35, gyroKd=0.0;

float plotrange[2] = {-10, 10};

double speedSetpoint, speedInput, speedOutput;
PID speedPID(&speedInput, &speedOutput, &speedSetpoint, speedKp, speedKi, speedKd, DIRECT);

double gyroySetpoint, gyroyInput, gyroyOutput;
PID gyroyPID(&gyroyInput, &gyroyOutput, &gyroySetpoint, gyroKp, gyroKi, gyroKd, DIRECT);

///////////////////   Setup Gyro with Combination Filter   /////////////////////

CFilter CFilterY; // Create the CFilter instances

double gyroX, gyroY, gyroZ;
int16_t tempRaw;
double  gyroYangle; // Angle calculate using the gyro only
double CFilteredlAngleY; // Calculated angle using a CFilter
double pitch,roll,gyroYrate, gyroangle;
uint32_t timer;
uint8_t i2cData[14]; // Buffer for I2C data
double gyroxoffset, gyroyoffset;
float forward, remoteclock, ac2, accXF;

/////////////////////////////     Setup Ultrasound    ///////////////////////////

float fping, pingval;
#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     11  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 400 // Maximum distance we want to ping for (in centimetres). Maximum sensor distance is rated at 400-500cm.
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.
RunningAverage USound(2);

////////////////// Setup Pins for Bluetooth  ///////////////////////////////////


SoftwareSerial BTSerial(17,16);  // RX, TX


/////////////////////          Setup Motors             /////////////////////////

// m1 is the T-Bot's right motor, m2 is the left

const int m1ndb = 23 , m1pdb = 23, m2ndb = 23 , m2pdb = 23; // note the values are always positive good for george
//const int m1ndb = 33 , m1pdb = 33, m2ndb = 33 , m2pdb = 33; // note the values are always positive good for B
//const int m1ndb = 32 , m1pdb = 31, m2ndb = 27 , m2pdb = 26; // good fot T-Bot
const int m2stby = 6, m2ain1 = 4, m2ain2 = 5, m2pwmpin = 9,  mpsfactor = 240, mpsfactor2 = 240;

Motor m1 = Motor(m2ain1, m2ain2, m2stby, m2pwmpin, m1ndb, m1pdb, mpsfactor);

const int m1stby = 6, m1ain1 = 8, m1ain2 = 7,  m1pwmpin = 10;
Motor m2 = Motor(m1ain1, m1ain2, m1stby, m1pwmpin, m2ndb, m2pdb, mpsfactor2);



/////////////////  Setup schedules  //////////////////////////////

void bluetoothCallBack();    // Bluetooth IO receive data
void sendDataCallBack();     // Bluetooth IO Send data
void printDataCallBack();    // Serial Print
void setTuningCallBack();    // Serial Print
void gyroPIDCallBack();      // Stability PID Control Loop
void speedPIDCallBack();     // Speed PID Control Loop
void CFilterReadCallBack();  // Filtered Angle Readback
void uSoundCallBack();       // Ultrasound Measure Loop
void autoTrimCallBack();     // Auto Trim on button press


Task bluetooth(2,TASK_FOREVER,&bluetoothCallBack);
Task bluetoothsend(120, TASK_FOREVER, &sendDataCallBack);
Task printData(50, TASK_FOREVER, &printDataCallBack);
Task setTuning(200, TASK_FOREVER, &setTuningCallBack);
Task tGyroPID(4, TASK_FOREVER, &gyroPIDCallBack);
Task tspeedPID(4, TASK_FOREVER, &speedPIDCallBack);
Task tCFilterRead(2,TASK_FOREVER, &CFilterReadCallBack);
Task uSound(60, TASK_FOREVER, &uSoundCallBack);
Task autoTrim(20, TASK_FOREVER, &autoTrimCallBack);
Scheduler runner;

void bluetoothCallBack(){

    if (BTSerial.available())
    {
        
      char character = BTSerial.read(); // Receive a single character from the software serial port
        
        if (character == STX){
          ii=0; 
        }
          if(ii > 0 && ii < 7 && character > 47 && character < 58){        
          array1[ii] = character;

          }

          if (ii == 7 && character > 64 && character < 91){
            array1[ii] = character;
          }
         
                ii+=1;
        }

          for(int loop1 = 0; loop1 < 8; loop1++) {
              data[loop1]= array1[loop1];
              }
              if (array1[7] > 64 && array1[7] < 91){
          letter =   array1[7];
              } 
              else{
                letter = 90;
                }

        if (ii == 7){
        setJoystick(data);
        
        
        }
         
    }
             
           


void uSoundCallBack(){
   // This is where you can setup the swarming rules 
   pingval = sonar.ping_cm();
   if (pingval == pingval){ //check pingval is not NAN
    if (pingval > 0){
   USound.addValue(pingval);
   fping = USound.getAverage();
   }
  if (fping > 0.1 && fping < 5){
   backoff = -70;
   }
  else{
    backoff = 0;
   }
  }
}



void sendDataCallBack(){

   BTSerial.print((char)STX);
   BTSerial.print(KPS);
   BTSerial.print((char)comma);
   BTSerial.print(KP);
   BTSerial.print((char)comma);
   BTSerial.print(gtrim);
   BTSerial.print((char)comma);
   //BTSerial.print(fping);
   BTSerial.print((CFilteredlAngleY-gtrim-plotrange[0])*(255/(plotrange[1]-plotrange[0]))); // the full plotting windoe is 0 to 255
   BTSerial.print((char)ETX);
  
}

void printDataCallBack(){
    Serial.print(joyXf); Serial.print("\t");
    Serial.print(joyYf); Serial.print("\t");
   // Serial.print(fping);Serial.print("\t");
   // Serial.print(KPS);Serial.print("\t");
   // Serial.print(KP);Serial.print("\t");
   // Serial.print(gtrim);Serial.print("\t");
   // Serial.print(CFilteredlAngleY);Serial.print("\t");
   // Serial.print(array1[7]);Serial.print("\t");
    Serial.print("\n");
}


void setTuningCallBack(){
    incflag = 1;
    refreshTuningFields(array1[7]);
    speedPID.SetTunings(KPS, speedKi, speedKd);
    gyroyPID.SetTunings(KP, KI, gyroKd);
    

}

void CFilterReadCallBack(){
    gyroread();

}


void speedPIDCallBack() {
  if (abs(joyXf)>60){ // Compensation to prevent robot falling over when spinning

        speedSetpoint = controller_sensitivity*((abs(joyYf)+90+backoff)/mpsfactor);
  }
  else{
        speedSetpoint = controller_sensitivity*((joyYf+backoff)/mpsfactor);
  }
  if (vxy != vxy){
    speedInput = 0;
  }
  else{
    speedInput = -vxy;
  }
    speedPID.Compute();
    v2ang(h, speedOutput);
    gyroySetpoint = angout;

 //   Serial.print(joyXf); Serial.print("\t");
 //   Serial.print(joyYf); Serial.print("\t");
 //   Serial.print("\n");

}

void gyroPIDCallBack() {
    gyroyInput = CFilteredlAngleY-(gtrim);// sign on GyroTrim to make +ve correspont to forward.
    gyroyPID.Compute();
    
    spinval = -spinfactor*joyXf/mpsfactor;
    vel(h,gyroyOutput); // output vxs, vys
    
    if (abs(CFilteredlAngleY)>60){
       m1.speed(spinval);
       m2.speed(spinval);
       boflag = 1; 
    }

    /////////// To help prevent brown out on the Bluetooth module when battery is low. //////////
    if (abs(gyroySetpoint)<0.5  && boflag == 1 && abs(vxy) < 0.1) {
       boflag = 0; 
    }

    
    if (boflag == 0){
      
    m1.speed((vxy-spinval+rtrim));
    m2.speed((vxy+spinval-rtrim));
    }  
}

void autoTrimCallBack(){
    if (abs(joyYf) < 0.1 && autotrim != 0){
      if (vxy > 0.01){
          gtrim += 0.01;
      }
      else if (vxy < 0.01){
        gtrim -= 0.01;
        
      }
      autotrim +=1;
    }
    
    if (autotrim > 100){
      autotrim = 0;
    } 
}

void setup()  
{
  Wire.begin();

  ////// Scale up PWM frequency to avoid annoying high pitch motor noise ///////

  int Eraser = 7; // this is 111 in binary and is used as an eraser  TCCRnB where n 
  int Prescaler = 1;// this could be a number in [1 , 6]. In this case, 3 corresponds in binary to 011.   
  TCCR1B &= ~Eraser; // this operation (AND plus NOT),  set the three bits in TCCR3B to 0
  TCCR1B |= Prescaler;//this operation (OR), replaces the last three bits in TCCR2B with our new value 011

  
  /////////////////////     Setup i2c commuication for Gyro       //////////////
 
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

  
  ////////////////           Set PID output limits       /////////////////////
  
    speedPID.SetOutputLimits(-0.2,0.2);
    speedPID.SetMode(AUTOMATIC);
    speedPID.SetSampleTime(speedpidsampletime);
  
    gyroyPID.SetOutputLimits(-60,60);
    gyroyPID.SetMode(AUTOMATIC);
    gyroyPID.SetSampleTime(gyropidsampletime);

  
    Serial.begin(38400);
    BTSerial.begin(38400);
    runner.init();
    
    runner.addTask(bluetooth);
    bluetooth.enable();
    
    runner.addTask(bluetoothsend);
    bluetoothsend.enable();
   
  //  runner.addTask(printData);
  //  printData.enable();
    
    runner.addTask(setTuning);
    setTuning.enable();
    
    runner.addTask(tCFilterRead);
    tCFilterRead.enable();
    
    runner.addTask(tspeedPID); // Add Speed PID control
    tspeedPID.enable();
    
    runner.addTask(tGyroPID);  // Add Stability PID control
    tGyroPID.enable();

    runner.addTask(uSound);    // Add Ultrasound Readback
    uSound.enable();

    runner.addTask(autoTrim);
    autoTrim.enable();
      
}

void loop () {
  runner.execute();
}
