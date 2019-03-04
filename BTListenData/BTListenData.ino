#include <SoftwareSerial.h>
#define    STX          0x02
#define    ETX          0x03
#define    comma        0x2C
byte xy[] = {STX, 50, 48, 48, 50, 48, 48, ETX};
byte letterA[] = {STX, 0, ETX};
byte array1[] = {STX, 50, 48, 48, 50, 48, 48, ETX};
char letter;
int joyX, joyY;
int ii, iii;
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
        if (character == STX){
          ii=0; 
        }
          array1[ii] = character;
                ii+=1;
        }
      Data = "";
      
      if (array1[2]==ETX){

          for(int loop1 = 0; loop1 < 3; loop1++) {
              letterA[loop1]= array1[loop1];
              
          }

      } 
      if (array1[7]==ETX && array1[2] != ETX){
          for(int loop2 = 0; loop2 < 8; loop2++) {
              xy[loop2]= array1[loop2];
          }
      
      }
   letter = letterA[1];
   joyX = (xy[1]-48)*100 + (xy[2]-48)*10 + (xy[3]-48);       // obtain the Int from the ASCII representation
   joyY = (xy[4]-48)*100 + (xy[5]-48)*10 + (xy[6]-48);

    if (joyX > 300 || joyY > 300){
      array1[1]=50;
      array1[4]=50;
    }
   if (iii > 50){
       
   BTSerial.print((char)STX);
   //BTSerial.print(fping);
   BTSerial.print(letter);
   BTSerial.print((char)comma);
   BTSerial.print(letter);
   BTSerial.print((char)comma);
   BTSerial.print(letter);
   BTSerial.print((char)comma);
 //  BTSerial.print(KI_last);
   BTSerial.print(joyY);
   BTSerial.print((char)ETX);
   iii = 0;
   }

    
    Serial.print(joyX); Serial.print("\t");
    Serial.print(joyY); Serial.print("\t");
    Serial.print(letter);Serial.print("\t");
    //Serial.print(ii);
    Serial.print("\n");
    
    iii+=1;
    

}
