#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <avr/wdt.h>

// CONFIGURACIÓN DE PINES

#define SS_PIN 10
#define RST_PIN 9

#define LED_GREEN 2
#define LED_WHITE 3
#define LED_RED   4

#define BUZZER 5
#define SERVO_PIN 6

// UID PERMITIDA
#define AUTH_UID "4A 87 F9 04"

// OBJETOS

MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x3F, 16, 2);
Servo servo;

// ESTADOS DE SISTEMA

bool puertaCerrada = true;

int failedCount = 0;

bool alarmMode = false;
bool alarmLocked = false;
unsigned long alarmStart = 0;
unsigned long lastToggle = 0;
bool buzOn = false;

const unsigned long countdownDuration = 5000;
const unsigned long buzFast = 120;
const unsigned long buzSlow = 400;

// Sistema
unsigned long lastHeartbeat = 0;
unsigned long heartbeatInterval = 1000;

// REINICIO RFID

void reiniciarRFID() {
  Serial.println("[SYS] Reiniciando modulo RFID...");
  mfrc522.PCD_Reset();
  delay(10);
  mfrc522.PCD_Init();
  delay(50);
  Serial.println("[SYS] RFID restaurado.");
}

// LCD ANIMADA 

void lcdHackerAnim(const char* msg) {
  lcd.clear();
  lcd.setCursor(0,0);

  for (int i = 0; i < strlen(msg); i++) {
    lcd.print(msg[i]);
    delay(40);
  }
}

// HEARTBEAT — señal viva para Python

void heartbeat() {
  if (millis() - lastHeartbeat >= heartbeatInterval) {
    lastHeartbeat = millis();
    Serial.println("[HB] OK");
  }
}

// SETUP

void setup() {
  wdt_enable(WDTO_2S);

  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();

  lcd.init();
  lcd.backlight();
  lcd.clear();

  servo.attach(SERVO_PIN);
  servo.write(0);

  pinMode(LED_WHITE, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  digitalWrite(LED_WHITE, HIGH);

  lcd.clear();
  lcd.print(" Access Control ");
  lcd.setCursor(0,1);
  lcd.print("Scan Your Card>");

  Serial.println("=====================================");
  Serial.println(" SISTEMA RFID");
  Serial.println(" AUTODIAGNOSTICO INICIAL...");
  Serial.println("=====================================");

  delay(700);

  Serial.println("[OK] Watchdog habilitado.");
  Serial.println("[OK] LCD online.");
  Serial.println("[OK] Lector RFID inicializado.");
  Serial.println("[OK] Servo calibrado.");
  Serial.println("[OK] LEDS operativos.");
  Serial.println("[OK] Sistema funcionando.");
  Serial.println("-------------------------------------");
}

// DETECTAR UID

String leerUID() {

  if (!mfrc522.PICC_IsNewCardPresent()) return "";

  if (!mfrc522.PICC_ReadCardSerial()) return "";

  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
    if (i < mfrc522.uid.size - 1) uid += " ";
  }
  uid.toUpperCase();

  Serial.print("[RFID] UID detectado: ");
  Serial.println(uid);

  return uid;
}

// ACCESOS

void accesoPermitido() {

  lcdHackerAnim("ACCESO OK...");
  lcd.setCursor(0,1);
  lcd.print("ABRIENDO...");

  digitalWrite(LED_GREEN, HIGH);

  tone(BUZZER, 2000);
  delay(100);
  noTone(BUZZER);
  digitalWrite(LED_GREEN, LOW);

  if (puertaCerrada) {
    servo.write(100);
    puertaCerrada = false;
  } else {
    servo.write(0);
    puertaCerrada = true;
  }

  Serial.println("[ACCESS] ACCESO_OK");
  delay(1200);

  lcdHackerAnim("SCAN CARD...");
}

void accesoDenegado() {

  lcdHackerAnim("ACCESO DENEGADO");

  digitalWrite(LED_RED, HIGH);
  tone(BUZZER, 1500);
  delay(120);
  noTone(BUZZER);
  digitalWrite(LED_RED, LOW);

  Serial.println("[ACCESS] ACCESO_DENEGADO");

  delay(700);
  lcdHackerAnim("SCAN CARD...");
}

//        ALARMA 

void iniciarCuentaRegresiva() {
  alarmMode = true;
  alarmLocked = false;
  alarmStart = millis();
  lastToggle = 0;
  buzOn = false;

  servo.write(0);

  Serial.println("[ALARM] INICIANDO CUENTA REGRESIVA");
  lcdHackerAnim("ALARMA EN 5s");
}


void detenerAlarma() {
  alarmMode = false;
  alarmLocked = false;
  failedCount = 0;

  noTone(BUZZER);
  digitalWrite(LED_RED, LOW);

  lcdHackerAnim("ALARMA OFF");

  int tones[] = {1200, 1000, 800, 600, 400};
  for (int t : tones) {
    tone(BUZZER, t);
    digitalWrite(LED_GREEN, HIGH);
    delay(80);
    noTone(BUZZER);
    digitalWrite(LED_GREEN, LOW);
    delay(40);
  }

  servo.write(100);
  puertaCerrada = false;

  Serial.println("[ALARM] DESACTIVADA POR TARJETA OK");
  delay(600);

  lcdHackerAnim("SCAN CARD...");
}


// RUTINA DE ALARMA (NO BLOQUEANTE)

void alarmTick() {

  if (!alarmMode && !alarmLocked) return;

  unsigned long now = millis();


  // CUENTA REGRESIVA ACTIVA

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
      alarmMode = false;
      alarmLocked = true;

      digitalWrite(LED_RED, LOW);
      noTone(BUZZER);

      lcdHackerAnim("ALARMA ACTIVADA");
      Serial.println("[ALARM] BLOQUEADA");
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


// LOOP PRINCIPAL

void loop() {
  wdt_reset();
  heartbeat();
  alarmTick();

  // Detectar si el lector murió
  if (mfrc522.PCD_ReadRegister(mfrc522.VersionReg) == 0x00) {
    reiniciarRFID();
  }

  // Leer tarjeta
  String uid = leerUID();
  if (uid == "") return;

  // MODO DE ALARMA

  if (alarmMode || alarmLocked) {

    if (uid == AUTH_UID) {
      detenerAlarma();
      accesoPermitido();
    } 
    else {
      lcdHackerAnim("ALARMA ACTIVA");
      lcd.setCursor(0,1);
      lcd.print("SOLO TARJETA OK");

      Serial.println("[ALARM] TARJETA NO AUTORIZADA DURANTE ALARMA");

      delay(800);
    }

    mfrc522.PICC_HaltA();
    return;
  }

  // TARJETA AUTORIZADA

  if (uid == AUTH_UID) {
    accesoPermitido();
    failedCount = 0;
    mfrc522.PICC_HaltA();
    return;
  }

  // TARJETA DENEGADA

  accesoDenegado();
  failedCount++;

  Serial.print("[ACCESS] Intentos fallidos: ");
  Serial.println(failedCount);

  if (failedCount >= 3 && !alarmMode && !alarmLocked) {
    iniciarCuentaRegresiva();
  }

  mfrc522.PICC_HaltA();
}

//DEBUG EXTENDIDO 

void printSystemStatus() {
  Serial.println("----- ESTADO DEL SISTEMA -----");
  Serial.print("Puerta cerrada: "); Serial.println(puertaCerrada);
  Serial.print("Intentos fallidos: "); Serial.println(failedCount);
  Serial.print("Modo alarma: "); Serial.println(alarmMode);
  Serial.print("Alarma bloqueada: "); Serial.println(alarmLocked);
  Serial.println("--------------------------------");
}

//ANIMACIÓN SOLO PARA TEST 

void lcdBootAnimation() {

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("INICIALIZANDO...");
  delay(500);

  char frames[4] = {'|', '/', '-', '\\'};

  for (int i = 0; i < 10; i++) {
    lcd.setCursor(15, 1);
    lcd.print(frames[i % 4]);
    delay(100);
  }

  lcd.clear();
  lcd.print("OK SISTEMA LISTO");
  delay(500);
}

//EFECTO LUCES DE SEGURIDAD 

void flashSecurityLights() {
  for (int i = 0; i < 4; i++) {
    digitalWrite(LED_RED, HIGH);
    delay(80);
    digitalWrite(LED_RED, LOW);
    delay(80);
  }
}

//EFECTO "PUERTA MECANICA" 
void servoMechanicalEffect(int pos1, int pos2) {
  for (int i = pos1; i <= pos2; i += 5) {
    servo.write(i);
    delay(25);
  }
}

//EFECTO "CAMBIO DE ESTADO" EN SERIAL

void serialEventLog(const char* msg) {
  Serial.print("[LOG] ");
  Serial.println(msg);
}


//EFECTO SONIDO COMPLETO (NO USADO DIRECTO)

void bipSequence() {
  int tones[] = {900, 1200, 600, 300};
  for (int t = 0; t < 4; t++) {
    tone(BUZZER, tones[t]);
    delay(100);
    noTone(BUZZER);
    delay(50);
  }
}

// ============================================================
//               Fin del archivo 
// ============================================================
/*
   Codigo COMPLETO RFID + ALARMA
   — LECTOR AUTORECUPERABLE
   — WATCHDOG DE 2 SEGUNDOS
   — ALARMA CON CUENTA REGRESIVA + BLOQUEO
   — SONIDOS PERSONALIZADOS
   — LUCES LED INDICADORAS
   — LCD I2C CON EFECTO HACKER
   — COMPATIBLE CON INTERFAZ PYTHON 
*/
