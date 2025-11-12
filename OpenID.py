dejaaa mejor saca el sonido de autodestruccion #include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <avr/wdt.h>

#define SS_PIN 10
#define RST_PIN 9
#define LED_G 5
#define LED_R 4
#define BUZZER 2
MFRC522 mfrc522(SS_PIN, RST_PIN);
Servo myServo;

#define DENIED_UID_1 " 01 02 03 04"
#define AUTHORIZED_UID_1 " 4A 87 F9 04"

bool puertaCerrada = false;

// Contadores y estados de alarma
int failedCount = 0;
bool alarmMode = false;       // true durante la cuenta regresiva
bool alarmLocked = false;     // true cuando la alarma queda bloqueada y suena hasta tarjeta autorizada
unsigned long alarmStart = 0;
const unsigned long countdownDuration = 5000UL; // 5 segundos de "secuencia de autodestrucción" (acortado)
unsigned long lastToggle = 0;
bool buzOn = false;
const unsigned long buzIntervalFast = 120;   // intervalo para la secuencia rápida (ms)
const unsigned long buzIntervalSlow = 400;   // intervalo para la alarma bloqueada (ms)
const int SERVO_LOCK_POS = 0;    // posición fija del servo durante alarma
const int SERVO_NORMAL_POS = 180; // posición "segura" por defecto

void reiniciarRFID() {
  // Esta función reinicia el lector si se cuelga
  mfrc522.PCD_Reset();
  mfrc522.PCD_Init();
  delay(50);
}

void setup()
{
  wdt_enable(WDTO_2S); // reinicio automatico despues de 2 segundos si no se hace wdt_reset()
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  myServo.attach(3);

  myServo.write(SERVO_NORMAL_POS);

  pinMode(LED_G, OUTPUT);
  pinMode(LED_R, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  Serial.println("Sistema Listo - Siempre Vigilante");
}

void loop()
{
  wdt_reset();  // "Patada" al watchdog → evita el reinicio

  // Si el lector no está respondiendo, lo reiniciamos
  if (mfrc522.PCD_ReadRegister(mfrc522.VersionReg) == 0x00) {
    reiniciarRFID();
  }

  // Siempre procesamos la lógica de alarma (no bloqueante) para poder leer tarjetas mientras suena
  alarmTick();

  if (!mfrc522.PICC_IsNewCardPresent()) {
    // No hay tarjeta → continuar escuchando sin cortar el loop
    return;
  }

  if (!mfrc522.PICC_ReadCardSerial()) {
    // Fallo en lectura pero el programa sigue
    return;
  }

  String content = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    content.concat(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
    content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  content.toUpperCase();

  Serial.print("UID Detectado: ");
  Serial.println(content);

  // Si estamos en modo alarma bloqueada y aparece la tarjeta autorizada -> apagar alarma
  if (alarmMode || alarmLocked) {
    if (content == AUTHORIZED_UID_1) {
      detenerAlarmaPorTarjetaAutorizada();
      // también actuamos como acceso autorizado normal (toggle puerta)
      digitalWrite(LED_G, HIGH);
      tone(BUZZER, 1200); delay(120);
      tone(BUZZER, 1000); delay(120);
      noTone(BUZZER);
      digitalWrite(LED_G, LOW);

      if (puertaCerrada) {
        myServo.write(SERVO_NORMAL_POS);
        puertaCerrada = false;
        Serial.println("Puerta ABIERTA.");
      } else {
        myServo.write(SERVO_LOCK_POS == 0 ? 0 : SERVO_LOCK_POS); // no cambiar si prefieres
        puertaCerrada = true;
        Serial.println("Puerta CERRADA.");
      }

      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
      return;
    } else {
      // En modo alarma bloqueada, cualquier otra tarjeta no hace nada (silencio no se restablece)
      Serial.println("Alarma activa. Solo tarjeta autorizada apaga la alarma.");
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
      return;
    }
  }

  // TARJETA AUTORIZADA (modo normal)
  if (content == AUTHORIZED_UID_1) {

    digitalWrite(LED_G, HIGH);
    tone(BUZZER, 1200); delay(120);
    tone(BUZZER, 1000); delay(120);
    noTone(BUZZER);
    digitalWrite(LED_G, LOW);

    // resetear contador de fallos
    failedCount = 0;

    if (puertaCerrada) {
      myServo.write(SERVO_NORMAL_POS);
      puertaCerrada = false;
      Serial.println("Puerta ABIERTA.");
    } else {
      myServo.write(0);
      puertaCerrada = true;
      Serial.println("Puerta CERRADA.");
    }

  } else {
    // TARJETA DENEGADA
    failedCount++;
    digitalWrite(LED_R, HIGH);
    tone(BUZZER, 600); delay(350);
    noTone(BUZZER);
    digitalWrite(LED_R, LOW);

    Serial.print("ACCESO DENEGADO. Intentos fallidos: ");
    Serial.println(failedCount);

    // Si hay 3 intentos fallidos, iniciar secuencia de "autodestrucción"
    if (failedCount >= 3 && !alarmMode && !alarmLocked) {
      iniciarSecuenciaAutodestruccion();
    }
  }

  // Limpia la tarjeta de la memoria
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

// Inicia la secuencia (cuenta regresiva) que luego deja la alarma bloqueada
void iniciarSecuenciaAutodestruccion() {
  alarmMode = true;
  alarmLocked = false;
  alarmStart = millis();
  lastToggle = 0;
  buzOn = false;
  // Poner servo en posición fija de bloqueo desde el inicio
  myServo.write(SERVO_LOCK_POS);
  Serial.println(">>> SECUENCIA DE AUTODESTRUCCION INICIADA <<<");
}

// Rutina no bloqueante que maneja la cuenta regresiva + alarma bloqueada
void alarmTick() {
  if (!alarmMode && !alarmLocked) return;

  unsigned long now = millis();

  // DURANTE LA CUENTA REGRESIVA: efectos rápidos, parpadeo LED y zumbidos rápidos
  if (alarmMode && !alarmLocked) {
    unsigned long elapsed = now - alarmStart;
    if (now - lastToggle >= buzIntervalFast) {
      lastToggle = now;
      if (buzOn) {
        noTone(BUZZER);
        digitalWrite(LED_R, LOW);
        buzOn = false;
      } else {
        tone(BUZZER, 1500);
        digitalWrite(LED_R, HIGH);
        buzOn = true;
      }
      // Servo ya quedó fijo en iniciarSecuenciaAutodestruccion()
    }

    // Mostrar tiempo restante en serial cada segundo (opcional)
    static unsigned long lastMsg = 0;
    if (now - lastMsg >= 1000) {
      lastMsg = now;
      unsigned long remaining = (elapsed >= countdownDuration) ? 0 : (countdownDuration - elapsed) / 1000;
      Serial.print("Cuenta regresiva: ");
      Serial.print(remaining);
      Serial.println(" s");
    }

    // Cuando termina la cuenta regresiva -> pasar a alarma bloqueada
    if (elapsed >= countdownDuration) {
      alarmLocked = true;
      alarmMode = false;
      noTone(BUZZER);
      digitalWrite(LED_R, LOW);
      buzOn = false;
      delay(100);
      Serial.println(">>> ALARMA BLOQUEADA. Solo tarjeta autorizada la apaga. <<<");
      // Aseguramos servo en posición de bloqueo
      myServo.write(SERVO_LOCK_POS);
    }

    return;
  }

  // MODO ALARMA BLOQUEADA: patrón intermitente más lento y persistente; servo queda fijo
  if (alarmLocked) {
    if (now - lastToggle >= buzIntervalSlow) {
      lastToggle = now;
      if (buzOn) {
        noTone(BUZZER);
        digitalWrite(LED_R, LOW);
        buzOn = false;
      } else {
        tone(BUZZER, 900);
        digitalWrite(LED_R, HIGH);
        buzOn = true;
      }
      // Mantener servo en posición de "bloqueo"
      myServo.write(SERVO_LOCK_POS);
    }
  }
}

// Si aparece la tarjeta autorizada mientras hay alarma, la apagamos y reproducimos el "apagado de alarma de auto"
void detenerAlarmaPorTarjetaAutorizada() {
  alarmMode = false;
  alarmLocked = false;
  failedCount = 0;
  noTone(BUZZER);
  digitalWrite(LED_R, LOW);
  Serial.println("Alarma apagada por tarjeta autorizada. Reproduciendo sonido de apagado...");

  // Secuencia tipo "alarma de auto apagándose" - tonos descendentes cortos
  playCarAlarmShutdown();

  // Volver servo a posición normal (segura)
  myServo.write(SERVO_NORMAL_POS);
  Serial.println("Sistema normal.");
}

// Secuencia de apagado de alarma (puede ser bloqueante; es corta)
void playCarAlarmShutdown() {
  // ejemplo: varios tonos descendentes rápidos
  int tones[] = {1200, 1000, 850, 700, 550, 400};
  int n = sizeof(tones) / sizeof(tones[0]);
  for (int i = 0; i < n; i++) {
    tone(BUZZER, tones[i]);
    digitalWrite(LED_G, HIGH); // pequeño indicador
    delay(100);
    noTone(BUZZER);
    digitalWrite(LED_G, LOW);
    delay(60);
  }
  // un último "silencio" para cerrar
  noTone(BUZZER);
  digitalWrite(LED_G, LOW);
}
