#include <SoftwareSerial.h>

SoftwareSerial BTSerial(17, 16); // RX | TX

void setup()
{
 // pinMode(15, OUTPUT);  // this pin will pull the HC-05 pin 34 (key pin) HIGH to switch module to AT mode
 // digitalWrite(15, HIGH); //some modules require these lines to be commented out
  Serial.begin(9600);
  Serial.println(" ");
  Serial.println("Type AT+NAME:NewName to change your T-BOTS name.");
  Serial.println(" ");
  Serial.println("Type AT+NAME:NewName to change your T-BOTS name.");
  Serial.println(" ");
  Serial.println("Type AT+UART=57600,0,0 to change baud rate");
  Serial.println("Enter AT commands:");
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
