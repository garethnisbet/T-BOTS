#include <Motor.h>
float timer1, timer2;
// Setup Motors
// Set motor deadbands 
const int m1ndb = 0 , m1pdb = 0, m2ndb = 0 , m2pdb = 0;
//const int m1ndb = 34 , m1pdb = 34, m2ndb = 34 , m2pdb = 34; // T-Bot

// Set pins and meters per second factor
const int m2stby = 6, m2ain1 = 4, m2ain2 = 5, m2pwmpin = 9,  mpsfactor = 1;
Motor m1 = Motor(m2ain1, m2ain2, m2stby, m2pwmpin, m1ndb, m1pdb, mpsfactor);

const int m1stby = 6, m1ain1 = 8, m1ain2 = 7,  m1pwmpin = 10;
Motor m2 = Motor(m1ain1, m1ain2, m1stby, m1pwmpin, m2ndb, m2pdb, mpsfactor);

void setup() {
  int Eraser = 7; // this is 111 in binary and is used as an eraser  TCCRnB where n 
  int Prescaler = 1;// this could be a number in [1 , 5]. In this case, 3 corresponds in binary to 011.   
  TCCR1B &= ~Eraser; // this operation (AND plus NOT),  set the three bits in TCCR3B to 0
  TCCR1B |= Prescaler;//this operation (OR), replaces the last three bits in TCCR2B with our new value 011
Serial.begin(38400);
pinMode(2, OUTPUT);

}

void loop() {
//  m1.speed(0.3);
//  m2.speed(-0.3);
//  delay(2000);
  
 // m1.speed(70); // Right Motor
 // m2.speed(70);  // Left Motor
  timer1=millis();
  ////////////////// to show millis is still valid /////////////
  digitalWrite(2, HIGH);       // sets the digital pin 2 on
  delay(10);                  // waits for a second
  digitalWrite(2, LOW);        // sets the digital pin 2 off
  delay(10);                  // waits for a second
  timer2=millis();
//  Serial.print(timer2-timer1); Serial.print("\t");
//  Serial.print("\n");

}
