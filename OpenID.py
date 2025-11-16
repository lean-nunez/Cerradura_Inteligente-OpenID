#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <avr/wdt.h>

#define SS_PIN 10
#define RST_PIN 9

// Pines LEDS
#define LED_WHITE 3   // Led blanco → sistema funcionando
#define LED_GREEN 2   // Led verde  → acceso permitido
#define LED_RED   4   // Led rojo   → acceso denegado / alarma

#define BUZZER 5
#define SERVO_PIN 6

// UID autorizada (TU TARJETA)
#define AUTH_UID "4A 87 F9 04"

MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x3F, 16, 2);
Servo servo;

// ESTADOS
bool puertaCerrada = true;

int failedCount = 0;

bool alarmMode = false;       // cuenta regresiva
bool alarmLocked = false;     // alarma final
unsigned long alarmStart = 0;
unsigned long lastToggle = 0;
bool buzOn = false;

const unsigned long countdownDuration = 5000; // 5 segundos
const unsigned long buzFast = 120;
const unsigned long buzSlow = 400;

void reiniciarRFID() {
  mfrc522.PCD_Reset();
  delay(10);
  mfrc522.PCD_Init();
  delay(50);
}

void setup() {
  wdt_enable(WDTO_2S); // watchdog

  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();

  lcd.init();
  lcd.backlight();

  servo.attach(SERVO_PIN);
  servo.write(0); // puerta cerrada

  pinMode(LED_WHITE, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  // sistema encendido
  digitalWrite(LED_WHITE, HIGH);

  lcd.clear();
  lcd.print(" Access Control ");
  lcd.setCursor(0, 1);
  lcd.print("Scan Your Card>");
}

void loop() {
  wdt_reset();

  // Verificar lector congelado
  if (mfrc522.PCD_ReadRegister(mfrc522.VersionReg) == 0x00) {
    reiniciarRFID();
  }

  // Procesar alarma (no bloqueante)
  alarmTick();

  // Esperar tarjeta
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  // Obtener UID
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
    if (i < mfrc522.uid.size - 1) uid += " ";
  }
  uid.toUpperCase();

  Serial.print("UID detectado: ");
  Serial.println(uid);

  lcd.clear();
  lcd.print("Leyendo UID...");
  delay(300);

  // *** TARJETA PARA APAGAR LA ALARMA ***
  if (alarmMode || alarmLocked) {
    if (uid == AUTH_UID) {
      detenerAlarma();
      accesoPermitido();
    } else {
      lcd.clear();
      lcd.print("ALARMA ACTIVA");
      lcd.setCursor(0, 1);
      lcd.print("Solo tarjeta OK");
      delay(1200);
    }
    mfrc522.PICC_HaltA();
    return;
  }

  // *** TARJETA AUTORIZADA ***
  if (uid == AUTH_UID) {
    accesoPermitido();
    failedCount = 0;
  }

  else {
    // *** TARJETA DENEGADA ***
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

void accesoPermitido() {
  lcd.clear();
  lcd.print("Acceso Permitido");

  digitalWrite(LED_GREEN, HIGH);
  tone(BUZZER, 2000);
  delay(100);
  noTone(BUZZER);
  delay(80);
  digitalWrite(LED_GREEN, LOW);

  if (puertaCerrada) {
    servo.write(100);
    puertaCerrada = false;
  } else {
    servo.write(0);
    puertaCerrada = true;
  }

  delay(1000);

  lcd.clear();
  lcd.print("Scan Your Card>");
}

void accesoDenegado() {
  lcd.clear();
  lcd.print("Acceso Denegado");

  digitalWrite(LED_RED, HIGH);
  tone(BUZZER, 1500);
  delay(120);          // pitidos más cortos
  noTone(BUZZER);
  digitalWrite(LED_RED, LOW);

  delay(800);
  lcd.clear();
  lcd.print("Scan Your Card>");
}

// ============================================================
// ALARMA A — CUENTA REGRESIVA + ALARMA BLOQUEADA
// ============================================================

void iniciarCuentaRegresiva() {
  alarmMode = true;
  alarmLocked = false;
  alarmStart = millis();
  lastToggle = 0;
  buzOn = false;

  servo.write(0); // bloquear

  Serial.println(">> INICIANDO CUENTA REGRESIVA <<");

  lcd.clear();
  lcd.print("ALARMA EN 5s");
}

void alarmTick() {
  if (!alarmMode && !alarmLocked) return;

  unsigned long now = millis();

  // CUENTA REGRESIVA
  if (alarmMode && !alarmLocked) {

    unsigned long elapsed = now - alarmStart;

    if (now - lastToggle >= buzFast) {
      lastToggle = now;
      buzOn = !buzOn;
      digitalWrite(LED_RED, buzOn);
      if (buzOn) tone(BUZZER, 2000);
      else noTone(BUZZER);
    }

    if (elapsed >= countdownDuration) {
      // PASA A ALARMA BLOQUEADA
      alarmMode = false;
      alarmLocked = true;
      noTone(BUZZER);
      digitalWrite(LED_RED, LOW);
      lcd.clear();
      lcd.print("ALARMA ACTIVADA");
      Serial.println(">> ALARMA BLOQUEADA <<");
      delay(500);
    }
    return;
  }

  // ALARMA BLOQUEADA
  if (alarmLocked) {
    if (now - lastToggle >= buzSlow) {
      lastToggle = now;
      buzOn = !buzOn;
      digitalWrite(LED_RED, buzOn);
      if (buzOn) tone(BUZZER, 900);
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

  // efecto “apagado de alarma”
  int tones[] = {1200, 1000, 800, 600, 400};
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

  delay(700);
  lcd.clear();
  lcd.print("Scan Your Card>");
}
