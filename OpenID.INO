#include <Wire.h>
#include <SPI.h>
#include <MFRC522.h>
#include <RTClib.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

// --- PINS ---
#define SS_PIN      10
#define RST_PIN     9
#define LED_GREEN   2
#define LED_RED     3
#define SERVO_PIN   6

// Hardware objects
MFRC522 rfid(SS_PIN, RST_PIN);
RTC_DS3231 rtc;
LiquidCrystal_I2C lcd(0x27,16,2);
Servo puerta;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();

  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Inicializando...");

  if (! rtc.begin()) {
    lcd.setCursor(0,1);
    lcd.print("RTC NO DETECTADO");
    while (1);
  }

  puerta.attach(SERVO_PIN);
  puerta.write(0); // puerta cerrada inicialmente
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Sistema listo");
  delay(1000);
}

void loop() {
  // Espera a que pase tarjeta
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  // Obtener UID leído
  String uidStr = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uidStr += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    uidStr += String(rfid.uid.uidByte[i], HEX);
  }
  uidStr.toUpperCase();

  // Obtener fecha/hora
  DateTime now = rtc.now();
  char fechaHora[20];
  sprintf(fechaHora, "%04d-%02d-%02d %02d:%02d:%02d",
          now.year(), now.month(), now.day(),
          now.hour(), now.minute(), now.second());

  // Enviar al Python: UID + timestamp
  Serial.print(uidStr);
  Serial.print(",");
  Serial.println(fechaHora);

  // Espera la respuesta del Python (ACCEPT o DENIED)
  while (Serial.available() == 0) {
    // espera
  }
  String respuesta = Serial.readStringUntil('\n');
  respuesta.trim();

  if (respuesta == "ACCEPT") {
    // Acceso concedido
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Acceso CONCEDIDO");
    lcd.setCursor(0,1);
    lcd.print(fechaHora);
    // Mover servo abrir
    puerta.write(90);
    delay(2000);
    // Luego cerrar
    puerta.write(0);
  } else {
    // Acceso denegado
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, HIGH);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("ACCESO DENEGADO");
    lcd.setCursor(0,1);
    lcd.print(fechaHora);
    puerta.write(0);
  }

  // Pausa antes de siguiente lectura
  delay(1500);
  rfid.PICC_HaltA();
}
