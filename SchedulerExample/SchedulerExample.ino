#include "NewPing.h"
#include "RunningAverage.h"
#include <TaskScheduler.h>


/*In computer programming, a callback is a piece of executable code that is passed as an argument to other code,
  which is expected to call back (execute) the argument at some convenient time.*/

void pin2CallBack();             // Instantiate callbacks
void pin4CallBack();

Task setpin2(100,TASK_FOREVER, &pin2CallBack); // Define task name frequency, duration and point to callback
Task setpin4(200, TASK_FOREVER, &pin4CallBack);

Scheduler runner;

///////////////////// Define callbacks  /////////////////////

void pin2CallBack(){  
  digitalWrite(2, HIGH);       // sets the digital pin 2 on
  delay(5);                  // waits for a second
  digitalWrite(2, LOW);        // sets the digital pin 2 off

  }

void pin4CallBack(){  
  digitalWrite(4, HIGH);       // sets the digital pin 2 on
  delay(5);                  // waits for a second
  digitalWrite(4, LOW);        // sets the digital pin 2 off
  }


void setup(){
Serial.begin(38400);
pinMode(2, OUTPUT);
pinMode(4, OUTPUT);

// initialise scheduled tasks
runner.init();
runner.addTask(setpin2);
runner.addTask(setpin4);

}
void loop(){
    // run schedule 
    runner.execute(); 
}
