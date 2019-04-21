#include <SoftwareSerial.h>

SoftwareSerial BTSerial(17, 16); // RX | TX
int XC = 500, YC = 500;
String Data = "";
#define    STX          0x02
#define    ETX          0x03

int X, X_old, Y, Y_old, dval = 0;
#define X_Pin  A6  // Analog X
#define Y_Pin  A7  // Analog Y

#define D_Pin  3  // Digital

void setup(){
Serial.begin(38400);
BTSerial.begin(38400);
}

void loop(){
   X = ((200/1034.)*analogRead(X_Pin))+100;
   Y = ((200/1034.)*analogRead(Y_Pin))+100;
   dval = digitalRead(D_Pin);
  // Serial.print(Data); Serial.print('\t');
 //  Serial.print(Y); Serial.print('\t');
 //  Serial.print('M'); Serial.print('\t');
 //  Serial.print('\n');
   if (X != X_old || Y != Y_old){
 //  BTSerial.print((char)STX);
 //  BTSerial.print(X);
 //  BTSerial.print(Y);
 //  BTSerial.print('Z');
   
   BTSerial.print((char)ETX);
   X_old = X;
   Y_old = Y;
 //  BTSerial.flush();
   }
   
if (BTSerial.available())
    {
        String character = BTSerial.readString(); // Receive a string
            Serial.print(character);Serial.print('\n');
        
    }
  
   
}
