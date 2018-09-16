#include <NewPing.h>
#include <RunningAverage.h>
float avg_ping, pingval;
#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     11  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 400 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.
RunningAverage USound(10);
void setup(){
Serial.begin(38400);
}

void loop(){

   pingval = sonar.ping_cm();  // Read distance from sensor
   if (pingval == pingval){    // Check pingval is not NAN
      if (pingval > 0){
        
          USound.addValue(pingval);
          avg_ping = USound.getAverage();
        
         }
    }
   
   Serial.print(pingval); Serial.print('\t');
   Serial.print(avg_ping); Serial.print('\t');  
   Serial.print('\n');
   
}
