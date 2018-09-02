#include <SoftwareSerial.h>

SoftwareSerial BTSerial(17, 16); // RX | TX

void setup()
{
 // pinMode(15, OUTPUT);  // this pin will pull the HC-05 pin 34 (key pin) HIGH to switch module to AT mode
 // digitalWrite(15, HIGH); //some modules require these lines to be commented out
  Serial.begin(9600);
  Serial.println("Commands for HC-05");
  Serial.println("Type AT+NAME:NewName to change your T-BOTS name.");
  Serial.println("Type AT+UART=57600,0,0 to change baud rate");
  Serial.println(" ");
  Serial.println(" ");
  Serial.println("Commands for AT-09");
  Serial.println("Type AT+NAMENewName to change your T-BOTS name.");
  Serial.println("Type AT+TYPE1 to enable PIN requirement.");
  Serial.println("Type AT+PIN123456 to set pin to 123456.");
  Serial.println("Type AT+BAUD7 to set BAUD rate to 57600.");
  Serial.println(" ");
  Serial.println(" ");
  Serial.println("Enter AT commands:");
  
  // HC-05 default BAUD rate is 38400 for AT command mode
  // AT-09 default BAUD rate is 9600. There is no default AT mode BAUD rate
  // so BTSerial.begin(38400) will have to be changed to BTSerial.begin(57600)
  // and uploaded again to the T-Bot if you want to continue in AT mode after 
  // issuing AT+BAUD7

  BTSerial.begin(38400);  // HC-05 default speed in AT command more
  //BTSerial.begin(9600);
}

void loop()
{
  // Keep reading from HC-05 and send to Arduino Serial Monitor
  if (BTSerial.available())
    Serial.write(BTSerial.read());

  // Keep reading from Arduino Serial Monitor and send to HC-05
  if (Serial.available())
    BTSerial.write(Serial.read());
}
