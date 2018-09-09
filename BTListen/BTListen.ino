#include <SoftwareSerial.h>

SoftwareSerial BTSerial(17,16);  // RX, TX
String Data = "";

void setup()  
{
    Serial.begin(38400);
    BTSerial.begin(38400);
    
}

void loop() // run over and over
{
    while (BTSerial.available())
    {
        char character = BTSerial.read(); // Receive a single character from the software serial port
        Data.concat(character); // Add the received character to the receive buffer
            Serial.println(Data);

            // Add your code to parse the received line here....

            // Clear receive buffer so we're ready to receive the next line
            Data = "";
        
    }
}
