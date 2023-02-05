int ain1 = 8, ain2 = 7, stby = 6, pwmpin = 10;


int pwm_width, theta = 0;

void setup() {
        pinMode(ain1, OUTPUT);
        pinMode(ain2, OUTPUT);
        pinMode(stby, OUTPUT);
        pinMode(pwmpin, OUTPUT);
        digitalWrite(stby, HIGH);
        
  //-------------------------------------------------------------------------------------//
  //----------- Scale up PWM frequency to avoid annoying high pitch motor noise ---------//
  //-------------------------------------------------------------------------------------//
  
  int Eraser = 7; // this is 111 in binary and is used as an eraser  TCCRnB where n 
  int Prescaler = 2;// this could be a number in [1 , 5]. In this case, 3 is the default and corresponds in binary to 011.   
  TCCR1B &= ~Eraser; // this operation (AND plus NOT),  set the three bits in TCCR3B to 0
  TCCR1B |= Prescaler;//this operation (OR), replaces the last three bits in TCCR2B with our new value 011

}
void loop() {

        theta += 1;
        pwm_width = sin(theta*3.14/180)*255;
        if (pwm_width <= 0){
            digitalWrite(ain1, LOW);
            digitalWrite(ain2, HIGH);  
        }
        else{
            digitalWrite(ain1, HIGH);
            digitalWrite(ain2, LOW);
             }

        analogWrite(pwmpin, abs(pwm_width));
        if (theta >= 360){
          theta = 0; 
        }
        
        delay(100);
        
        
}
