int Taster_1 = 11;
int Taster_2 = 10;
int Taster_3 = 9;
int Taster_4 = 8;
int LED = 13;
int state;


void setup() {
  // put your setup code here, to run once:

    pinMode(Taster_1, INPUT);  //X Richtung +
    pinMode(Taster_2, INPUT);  //X Richtung -
    pinMode(Taster_3, INPUT);  //Theta +
    pinMode(Taster_4, INPUT);  //Theta -
    pinMode(LED, OUTPUT);  //13 LED
    digitalWrite(LED, LOW);
    Serial.begin(115200);
    Serial.flush();
    delay(1000);
}

void loop() {
  // put your main code here, to run repeatedly:
    bool xPlus = digitalRead(Taster_1);
    bool xNega = digitalRead(Taster_2);
    bool thetaPlus = digitalRead(Taster_3);
    bool thetaNega = digitalRead(Taster_4);

    if (xPlus == HIGH && xNega == LOW && thetaPlus == LOW && thetaNega == LOW){
      state = 11;
    }
    else if (xPlus == LOW && xNega == HIGH && thetaPlus == LOW && thetaNega == LOW){
      state = 22;
    }
    else if (xPlus == LOW && xNega == LOW && thetaPlus == HIGH && thetaNega == LOW){
      state = 33;
    }
    else if (xPlus == LOW && xNega == LOW && thetaPlus == LOW && thetaNega == HIGH){
      state = 44;
    }
    else if (xPlus == HIGH && xNega == LOW && thetaPlus == HIGH && thetaNega == LOW){
      state = 55;
    }
    else if (xPlus == HIGH && xNega == LOW && thetaPlus == LOW && thetaNega == HIGH){
      state = 66;
    }
    else if (xPlus == LOW && xNega == HIGH && thetaPlus == HIGH && thetaNega == LOW){
      state = 77;
    }
    else if (xPlus == LOW && xNega == HIGH && thetaPlus == LOW && thetaNega == HIGH){
      state = 88;
    }
    else if (xPlus == LOW && xNega == LOW && thetaPlus == LOW && thetaNega == LOW){
      state = 0;
    }
    else {
      state = 0;
    }
    // LED13
    if (xPlus||xNega||thetaPlus||thetaNega) {
      digitalWrite(LED, HIGH);
    }
    else{
      digitalWrite(LED, LOW);
    }

    int len = Serial.println(state);
    delay(10);




     
}
