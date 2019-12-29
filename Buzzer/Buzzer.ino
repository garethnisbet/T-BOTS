
/* Arduino tutorial - Buzzer / Piezo Speaker
   More info and circuit: http://www.ardumotive.com/how-to-use-a-buzzer-en.html
   Dev: Michalis Vasilakis // Date: 9/6/2015 // www.ardumotive.com */

#include <NewTone.h>
const int buzzer = 2; //buzzer to arduino pin 2
int Hz, ii;

void setup(){
 
  pinMode(buzzer, OUTPUT); // Set buzzer - pin 2 as an output

}

void loop(){
  
  Hz = abs(sin(ii*3.14/180))*500; 
  tone(buzzer, Hz); // minimum 31 Hz
  delay(50);
  ii+=1;
  if (ii > 360){
    ii=0;
  }
  //tone(buzzer, 1000);
  //delay(2000);        // ...for 1sec
  
}
