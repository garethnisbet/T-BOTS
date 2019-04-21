int X = 0, Y = 0, dval = 0;

#define X_Pin  A6  // Analog X
#define Y_Pin  A7  // Analog Y

#define D_Pin  3  // Digital

void setup(){
Serial.begin(38400);
}

void loop(){
   X = analogRead(X_Pin);
   Y = analogRead(Y_Pin);
   dval = digitalRead(D_Pin);
   Serial.print(X); Serial.print('\t');
   Serial.print(Y); Serial.print('\t');
/*
   if (dval == HIGH){
    Serial.print(0); Serial.print('\t'); 
    }
    else{
    Serial.print(500); Serial.print('\t'); 
    }
    */
   Serial.print('\n');
   
}
