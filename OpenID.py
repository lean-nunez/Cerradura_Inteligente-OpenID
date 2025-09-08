
LiquidCrystal lcd(13, 11, 5, 4, 3, 2);


int m1 = 9;
int redLed = 12;
int greenLed = 7;
int m2 = 10;
int sucessButton = 8;
int failedButton = 6;

 
void setup()
{
  lcd.begin(16, 2);
  pinMode(sucessButton,INPUT);
  pinMode(failedButton,INPUT);
  pinMode(m1,OUTPUT);
  pinMode(m2,OUTPUT);
  pinMode(redLed,OUTPUT);
  pinMode(greenLed,OUTPUT);
  initialMessage();
}
 
void loop()
{
  if(digitalRead(sucessButton) == 1)
  {
    lcd.clear();
    lcd.print("Tarjeta Validada");
    lcd.setCursor(0,1);
    lcd.print("Exitosamente");
    digitalWrite(m1,HIGH);
    digitalWrite(greenLed,HIGH);
    delay(1000);
    initialMessage();
    digitalWrite(m1,LOW);
    digitalWrite(greenLed,LOW);
  }
  else if(digitalRead(failedButton) == 1)
  {
    lcd.clear();
    digitalWrite(redLed,HIGH);
    lcd.print("Tarjeta Validada");
    delay(1000);
    initialMessage();
    digitalWrite(redLed,LOW);
  }
}

void initialMessage()
{
  lcd.clear();
  lcd.print(" Acerca tu");  
  lcd.setCursor(0,1);
  lcd.print("Tarjeta o tag"); 
}
  