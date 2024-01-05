#include<LiquidCrystal.h>
LiquidCrystal lcd(8,9,10,11,12,13);
const int moistPin = A0, relayPin = 7;

void setup() {
  lcd.begin(16,2);
  pinMode(relayPin,OUTPUT);
  pinMode(moistPin,INPUT);
  digitalWrite(relayPin,HIGH);
  lcd.setCursor(0,0);
  lcd.print("Welcome to IIITS");
  lcd.setCursor(0,1);
  lcd.print(" IOT Evaluation ");
  delay(3000);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Project Guide : ");
  lcd.setCursor(0,1);
  lcd.print("Dr.AbhishekHazra");
  delay(3000);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Group Members : ");
  lcd.setCursor(0,1);
  lcd.print("Sampreeth, Akhil");
  delay(3000);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(" Charan, Rohith ");
  lcd.setCursor(0,1);
  lcd.print("   Sai Charan   ");
  delay(3000);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(" Automated Plant");
  lcd.setCursor(0,1);
  lcd.print(" Watering System");
  delay(3000);
  lcd.clear();
}

void loop() {
  int moist = analogRead(moistPin);
  int moist_per = map(moist , 0,1023, 100,0);
  lcd.setCursor(0,0);
  lcd.print("Moist:");
  lcd.print(moist_per);
  lcd.print("%");

  if(moist_per<=20){
    lcd.setCursor(0,1);
    lcd.print("   Pump : ON    ");
    digitalWrite(relayPin,LOW);
  }
  else{
    lcd.setCursor(0,1);
    lcd.print("   Pump : OFF   ");
    digitalWrite(relayPin,HIGH);
  }

  delay(200);
  lcd.clear();
  
}
