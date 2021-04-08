
#include "Arduino.h"
int ain1 = 4, ain2 = 5, stby = 6, pwmpin = 9;

void setup() {
        pinMode(ain1, OUTPUT);
        pinMode(ain2, OUTPUT);
        pinMode(stby, OUTPUT);
        pinMode(pwmpin, OUTPUT);
        digitalWrite(stby, HIGH);
}

void loop() {
        digitalWrite(ain1, HIGH);
        digitalWrite(ain2, LOW);
        analogWrite(pwmpin, 20);
        delay(2000);
        digitalWrite(ain1, LOW);
        digitalWrite(ain2, HIGH);
        analogWrite(pwmpin, 20);
        delay(2000);
}
