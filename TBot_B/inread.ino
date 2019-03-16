String inString = "";    // string to hold input
int currentVector = 0;


void inread() {
  int inChar;

  // Read serial input:
  if (Serial.available() > 0) {
    inChar = Serial.read();
  }

  if (isDigit(inChar)) {
    // convert the incoming byte to a char 
    // and add it to the string:
    inString += (char)inChar; 
  }

  // if you get a comma, convert to a number and increment the counter:
  if (inChar == ',') {

    switch (currentVector) {
    case 0:    // 0 = y
      kp = inString.toInt();
      // clear the string for new input:
      inString = ""; 
      break;
    case 1:    // 1 = z:
      ki = inString.toInt();
      // clear the string for new input:
      inString = ""; 
      break;
    }
    currentVector++;
  }

  if (inChar == '\n') {
    kd = inString.toInt();

    // clear the string for new input:
    inString = ""; 
    // reset the  counter:
    currentVector = 0;
  }

}

