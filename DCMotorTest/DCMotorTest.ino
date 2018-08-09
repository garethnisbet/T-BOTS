#include <Motor.h>
// Setup Motors
//const int m1ndb = 46 , m1pdb = 34, m2ndb = 24 , m2pdb = 21; // Foxy
//const int m1ndb = 30 , m1pdb = 37, m2ndb = 28 , m2pdb = 28; // Keir

//const int m1ndb = 23 , m1pdb = 27, m2ndb = -37 , m2pdb = 37; // Cinnamon
const int m1ndb = 24 , m1pdb = 24, m2ndb = 24 , m2pdb = 24; // Cinnamon
//const int m1ndb = 36 , m1pdb = 40, m2ndb = 20 , m2pdb = 28; // T-Bot
//const int m1ndb = 34 , m1pdb = 34, m2ndb = 34 , m2pdb = 34; // T-Bot-O
const int m2stby = 6, m2ain1 = 4, m2ain2 = 5, m2pwmpin = 9,  mpsfactor = 1;
Motor m1 = Motor(m2ain1, m2ain2, m2stby, m2pwmpin, m1ndb, m1pdb, mpsfactor);

const int m1stby = 6, m1ain1 = 8, m1ain2 = 7,  m1pwmpin = 10;
Motor m2 = Motor(m1ain1, m1ain2, m1stby, m1pwmpin, m2ndb, m2pdb, mpsfactor);

void setup() {
  int Eraser = 7; // this is 111 in binary and is used as an eraser  TCCRnB where n 
  int Prescaler = 1;// this could be a number in [1 , 6]. In this case, 3 corresponds in binary to 011.   
  TCCR1B &= ~Eraser; // this operation (AND plus NOT),  set the three bits in TCCR3B to 0
  TCCR1B |= Prescaler;//this operation (OR), replaces the last three bits in TCCR2B with our new value 011
Serial.begin(115200);

}

void loop() {
//  m1.speed(0.3);
//  m2.speed(-0.3);
//  delay(2000);
  
  m1.speed(-60); // Right Motor
  m2.speed(-60);  // Left Motor
 // delay(2000);
  // put your main code here, to run repeatedly:

}
