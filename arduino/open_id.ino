#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <avr/wdt.h>

#define SS_PIN 10
#define RST_PIN 9

// Pines LEDS
#define LED_WHITE 3
#define LED_GREEN 2
#define LED_RED   4

#define BUZZER 5
#define SERVO_PIN 6

MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo servo;

bool puertaCerrada = true;
int failedCount = 0;

bool alarmMode = false;
bool alarmLocked = false;
unsigned long alarmStart = 0;
unsigned long lastToggle = 0;
bool buzOn = false;

const unsigned long countdownDuration = 5000;
const unsigned long buzFast = 120;
const unsigned long buzSlow = 300;

// ================================
void mostrarEstadoPuerta() {
  lcd.clear();
  if (puertaCerrada) lcd.print("PUERTA CERRADA");
  else lcd.print("PUERTA ABIERTA");
  delay(1000);
}
// ================================

void reiniciarRFID() {
  mfrc522.PCD_Reset();
  delay(10);
  mfrc522.PCD_Init();
  delay(50);
}

void setup() {
  wdt_enable(WDTO_2S);

  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();

  lcd.init();
  lcd.backlight();

  servo.attach(SERVO_PIN);
  servo.write(0);

  pinMode(LED_WHITE, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  digitalWrite(LED_WHITE, HIGH);

  lcd.clear();
  lcd.print(" Access Control ");
  lcd.setCursor(0, 1);
  lcd.print("Scan Your Card>");
}

void loop() {
  wdt_reset();

  if (mfrc522.PCD_ReadRegister(mfrc522.VersionReg) == 0x00) {
    reiniciarRFID();
  }

  alarmTick();

  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
    if (i < mfrc522.uid.size - 1) uid += " ";
  }
  uid.toUpperCase();

  lcd.clear();
  lcd.print("Leyendo UID...");
  delay(300);

  // Enviar UID a Python
  Serial.println(uid);

  // Esperar respuesta
  while (!Serial.available()) {}

  String resp = Serial.readStringUntil('\n');
  resp.trim();

  // RESPUESTAS POSIBLES:
  // OK;Nombre;Apellido
  // NO;;
  // ADMIN_MODE

  if (resp == "ADMIN_MODE") {
    lcd.clear();
    lcd.print("** MODO ADMIN **");
    delay(1500);
    mfrc522.PICC_HaltA();
    return;
  }

  // Procesar respuesta normal
  int p1 = resp.indexOf(';');
  int p2 = resp.indexOf(';', p1 + 1);

  String estado = resp.substring(0, p1);
  String nombre = resp.substring(p1 + 1, p2);
  String apellido = resp.substring(p2 + 1);

  if (estado == "OK") {
    accesoPermitido(nombre, apellido);
    failedCount = 0;
  } else {
    accesoDenegado();
    failedCount++;
    if (failedCount >= 3 && !alarmMode) {
      iniciarCuentaRegresiva();
    }
  }

  mfrc522.PICC_HaltA();
}

// ============================================================
// FUNCIONES DE ACCESO
// ============================================================

void accesoPermitido(String nombre, String apellido) {
  lcd.clear();
  lcd.print("ACCESO OK");
  delay(600);
  
  lcd.clear();
  lcd.print(nombre);
  lcd.setCursor(0, 1);
  lcd.print(apellido);
  delay(1200);

  digitalWrite(LED_GREEN, HIGH);
  tone(BUZZER, 2200);
  delay(120);
  noTone(BUZZER);
  digitalWrite(LED_GREEN, LOW);

  if (puertaCerrada) {
    servo.write(100);
    puertaCerrada = false;
  } else {
    servo.write(0);
    puertaCerrada = true;
  }

  mostrarEstadoPuerta();

  lcd.clear();
  lcd.print("Scan Your Card>");
}

void accesoDenegado() {
  lcd.clear();
  lcd.print("ACCESO DENEGADO");

  digitalWrite(LED_RED, HIGH);
  tone(BUZZER, 1800);
  delay(150);
  noTone(BUZZER);
  digitalWrite(LED_RED, LOW);

  delay(800);
  lcd.clear();
  lcd.print("Scan Your Card>");
}

// ============================================================
// ALARMA
// ============================================================

void iniciarCuentaRegresiva() {
  alarmMode = true;
  alarmLocked = false;
  alarmStart = millis();
  lastToggle = 0;
  buzOn = false;

  servo.write(0);

  lcd.clear();
  lcd.print("ALARMA EN 5s");
}

void alarmTick() {
  if (!alarmMode && !alarmLocked) return;

  unsigned long now = millis();

  if (alarmMode && !alarmLocked) {
    unsigned long elapsed = now - alarmStart;

    if (now - lastToggle >= buzFast) {
      lastToggle = now;
      buzOn = !buzOn;
      digitalWrite(LED_RED, buzOn);
      if (buzOn) tone(BUZZER, 2800);
      else noTone(BUZZER);
    }

    if (elapsed >= countdownDuration) {
      alarmMode = false;
      alarmLocked = true;
      noTone(BUZZER);
      digitalWrite(LED_RED, LOW);
      lcd.clear();
      lcd.print("ALARMA ACTIVADA");
    }
    return;
  }

  if (alarmLocked) {
    if (now - lastToggle >= buzSlow) {
      lastToggle = now;
      buzOn = !buzOn;
      digitalWrite(LED_RED, buzOn);
      if (buzOn) tone(BUZZER, 1500);
      else noTone(BUZZER);
    }
    servo.write(0);
  }
}

void detenerAlarma() {
  alarmMode = false;
  alarmLocked = false;
  failedCount = 0;

  noTone(BUZZER);
  digitalWrite(LED_RED, LOW);

  lcd.clear();
  lcd.print("ALARMA APAGADA");

  int tones[] = {1600, 1300, 1000, 700, 500};
  for (int t : tones) {
    tone(BUZZER, t);
    digitalWrite(LED_GREEN, HIGH);
    delay(80);
    noTone(BUZZER);
    digitalWrite(LED_GREEN, LOW);
    delay(50);
  }

  servo.write(100);
  puertaCerrada = false;

  mostrarEstadoPuerta();

  delay(700);
  lcd.clear();
  lcd.print("Scan Your Card>");
}
