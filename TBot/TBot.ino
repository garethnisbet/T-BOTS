
// Import libraries here
#include <TaskScheduler.h>
#include <Motor.h>
#include <PID_v1.h>
#include <Filters.h>
#include <NewPing.h>
#include "SoftwareSerial.h"
#include <RunningAverage.h> // Running average filter
#include <Wire.h>
#include "Combination_Filter.h" 
#define buzzer 2

/////////////////////////////     Setup Ultrasound    ///////////////////////////

float fping, pingval;
#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     11  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 250 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.
RunningAverage USound(5);

///////////////////////////// Setup Bluetooth Control   ///////////////////////////

#define    STX          0x02
#define    ETX          0x03

int joyX, joyY, joyXbefore, joyYbefore, joyXdiff, joyYdiff, GyroTrim;
float controller_sensitivity = 1.4;
float joyXf, joyYf;
float backoff;

SoftwareSerial BTSerial(17,16);                           // BlueTooth module: pin#2=TX pin#3=RX
byte cmd[8] = {0, 0, 0, 0, 0, 0, 0, 0};                   // bytes received
byte buttonStatus = 0;                                    // first Byte sent to Android device
String displayStatus = "----"; 

/////////////////////////////////////////////////////////////////////////////////

int starttime;
int kp, ki, kd; // for inread function
int gyrocounter, commandcounter;

float gyrocomp;
float forward, remoteclock, ac2, accXF;
float spinval;
float spinfactor = 0.8;
float filterFrequency = 1;  
float g = 9.81, pi = 3.1416, h = 0.08;
float dh, th, phi, v, vxy, vx, vy, vz, norm, vxs, vys, angout;
float accX, accY, accZ;


////////////////////  Speed and Stability tunings   /////////////////////////
float gtrim = 0.5;   // Compensated for drift in forward or reverse direction.
float rtrim = -0.02; // Compensated for rotational drift.

float filter_weighting = 0.03; // See Combination_Filter.h

float speedpidsampletime = 2;
float gyropidsampletime = 2;

double speedKp=0.10, speedKi=0, speedKd=0.0, KPS = 0.10, KP = 4.0, KI = 85, KPS_last, KP_last, KI_last;
double gyroKp=4.0, gyroKi=85, gyroKd=0.0;

double speedSetpoint, speedInput, speedOutput;
PID speedPID(&speedInput, &speedOutput, &speedSetpoint, speedKp, speedKi, speedKd, DIRECT);

double gyroySetpoint, gyroyInput, gyroyOutput;
PID gyroyPID(&gyroyInput, &gyroyOutput, &gyroySetpoint, gyroKp, gyroKi, gyroKd, DIRECT);


/////////////////////          Setup Motors             /////////////////////////

const int m1ndb = 23 , m1pdb = 28, m2ndb = 33 , m2pdb = 20; 
const int m2stby = 6, m2ain1 = 4, m2ain2 = 5, m2pwmpin = 9,  mpsfactor = 257;

Motor m1 = Motor(m2ain1, m2ain2, m2stby, m2pwmpin, m1ndb, m1pdb, mpsfactor);

const int m1stby = 6, m1ain1 = 8, m1ain2 = 7,  m1pwmpin = 10;
Motor m2 = Motor(m1ain1, m1ain2, m1stby, m1pwmpin, m2ndb, m2pdb, mpsfactor);

///////////////////   Setup Gyro with Combination Filter   /////////////////////

CFilter CFilterY; // Create the CFilter instances

double gyroX, gyroY, gyroZ;
int16_t tempRaw;
double  gyroYangle; // Angle calculate using the gyro only
double CFilteredlAngleY; // Calculated angle using a CFilter
double pitch,roll,gyroYrate;
uint32_t timer;
uint8_t i2cData[14]; // Buffer for I2C data
double gyroxoffset, gyroyoffset;

///////////////////          Setup Scheduled Tasks         /////////////////////

void CFilterReadCallBack();             // Filtered Angle Readback
void speedPIDCallBack();                // Speed PID Control Loop
void gyroPIDCallBack();                 // Stability PID Control Loop
void bluetoothCallBack();               // Bluetooth IO Read Loop
void uSoundCallBack();                  // Ultrasound Measure Loop
void printDataCallBack();               // Print Data to Serial Loop

///////////////////    Set Number of Loops and Frequency  /////////////////////

Task tCFilterRead(2,TASK_FOREVER, &CFilterReadCallBack);
Task tGyroPID(4, TASK_FOREVER, &gyroPIDCallBack);
Task tspeedPID(4, TASK_FOREVER, &speedPIDCallBack);
Task bluetooth(20,TASK_FOREVER,&bluetoothCallBack);
Task uSound(60, TASK_FOREVER, &uSoundCallBack);


Scheduler runner;


void uSoundCallBack(){    
   pingval = sonar.ping_cm();
   if (pingval == pingval){
   USound.addValue(pingval);
   fping = USound.getAverage();
   }
  if (fping > 0.1 && fping < 5){
   backoff = -50;
   }
  else{
    backoff = 0;
   }
}

void bluetoothCallBack(){
  if(BTSerial.available())  {                           // data received from smartphone
    //delay(2);
    cmd[0] =  BTSerial.read();  
    if(cmd[0] == STX)  {
      int i=1;      
      while(BTSerial.available())  {
       // delay(1);
        cmd[i] = BTSerial.read();
        if(cmd[i]>127 || i>7)                 break;     // Communication error
        if((cmd[i]==ETX) && (i==2 || i==7))   break;     // Button or Joystick data
        i++;
      }
      if     (i==2)          getButtonState(cmd[1]);    // 3 Bytes  ex: < STX "C" ETX >
      if(i==7)          getJoystickState(cmd);     // 6 Bytes  ex: < STX "200" "180" ETX >
    }
  }
  if (KPS + KP + KI !=  KPS_last + KP_last + KI_last){
    speedPID.SetTunings(KPS, speedKi, speedKd);
    gyroyPID.SetTunings(KP, KI, gyroKd);
  }
  KPS_last = speedPID.GetKp();
  KP_last = gyroyPID.GetKp();
  KI_last = gyroyPID.GetKi();

  
   BTSerial.print((char)STX);
   BTSerial.print((char)0x1);
   //BTSerial.print(fping);
   BTSerial.print(KPS_last);
   BTSerial.print((char)0x4);
   BTSerial.print(KP_last);
   BTSerial.print((char)0x5);
 //  BTSerial.print(KI_last);
   BTSerial.print(gtrim);
   BTSerial.print((char)ETX);

   
 
   
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
}

void gyroPIDCallBack() {
    gyroyInput = CFilteredlAngleY-(gtrim+GyroTrim*0.1);// sign on GyroTrim to make +ve correspont to forward.
    gyroyPID.Compute();
    
    spinval = -spinfactor*joyXf/mpsfactor;
    velxy(h,gyroyOutput); // output vxs, vys
    if (abs(CFilteredlAngleY)>40){
       m1.speed(spinval);
       m2.speed(spinval); 
    }
    else{
    m1.speed((vxy-spinval+rtrim));
    m2.speed((vxy+spinval-rtrim));
    }

    
}

void setup () {
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
  
  gyroyPID.SetOutputLimits(-90,90);
  gyroyPID.SetMode(AUTOMATIC);
  gyroyPID.SetSampleTime(gyropidsampletime);

  
  ///////////   Setup Serial and Bluetooth communication   ////////////////////

  // pinMode(15, OUTPUT);  // this pin will pull the HC-05 pin 34 (key pin) HIGH to switch module to AT mode
  // digitalWrite(15, LOW); //Some modules reqire this to be set to HIGH 
  // Others require these lines to be commented out.

  Serial.begin(9600);
  BTSerial.begin(38400);
  while(BTSerial.available())  BTSerial.read();

  
  /////////////////         Start Scheduled Tasks         /////////////////////

  runner.init();

  runner.addTask(tCFilterRead);
  runner.addTask(tspeedPID); // Add Speed PID control 
  runner.addTask(tGyroPID);  // Add Stability PID control
  runner.addTask(uSound);    // Add Ultrasound Readback
  runner.addTask(bluetooth); // Add Bluetooth Comunication
  
  tGyroPID.enable();  
  tspeedPID.enable();  
  uSound.enable();
  bluetooth.enable();
  tCFilterRead.enable();

}

void loop () {
  runner.execute();
}


