#include "NewPing.h"
#include "RunningAverage.h"
#include <TaskScheduler.h>


/*In computer programming, a callback is a piece of executable code that is passed as an argument to other code,
  which is expected to call back (execute) the argument at some convenient time.*/

void pin2CallBack();             // Instantiate callbacks
void pin3CallBack();

Task setpin2(6,TASK_FOREVER, &pin2CallBack); // Define task name frequency, duration and point to callback
Task setpin3(9, TASK_FOREVER, &pin3CallBack);

Scheduler runner;

///////////////////// Define callbacks  /////////////////////

void pin2CallBack(){  
  digitalWrite(2, HIGH);       // sets the digital pin 2 on
  delay(1);                  // waits for a second
  digitalWrite(2, LOW);        // sets the digital pin 2 off


  }

void pin3CallBack(){  
  digitalWrite(3, HIGH);       // sets the digital pin 2 on
  delay(1);                  // waits for a second
  digitalWrite(3, LOW);        // sets the digital pin 2 off

  }


void setup(){

Serial.begin(38400);
pinMode(2, OUTPUT);
pinMode(3, OUTPUT);

// initialise scheduled tasks
runner.init();
runner.addTask(setpin2);
runner.addTask(setpin3);
setpin2.enable();
setpin3.enable();

}
void loop(){
    // run schedule 
    runner.execute(); 
}
