#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <MFRC522.h>

#// Pines RC522
#define SS_PIN 21
#define RST_PIN 22

# MFRC522 mfrc522(SS_PIN, RST_PIN);

# // LCD I2C
# LiquidCrystal_I2C lcd(0x27, 16, 2);

# // Actuadores
# int m1 = 9;
# int redLed = 12;
# int greenLed = 7;

# // WiFi
# const char* ssid = "TU_WIFI";
# const char* password = "TU_PASS";

# // Servidor PHP
# String server = "http://TU_SERVIDOR/insert_scan.php";

# void setup() {
#   Serial.begin(115200);

#   // Inicializar LCD
#   lcd.init();
#   lcd.backlight();
#   initialMessage();

#   // Pines
#   pinMode(m1, OUTPUT);
#   pinMode(redLed, OUTPUT);
#   pinMode(greenLed, OUTPUT);

#   // Inicializar RC522
#   SPI.begin();
#   mfrc522.PCD_Init();

#   // Conectar WiFi
#   WiFi.begin(ssid, password);
#   while (WiFi.status() != WL_CONNECTED) {
#     delay(500);
#     Serial.print(".");
#   }
#   Serial.println("Conectado a WiFi!");
# }

# void loop() {
#   // Esperar tarjeta
#   if (!mfrc522.PICC_IsNewCardPresent()) return;
#   if (!mfrc522.PICC_ReadCardSerial()) return;

#   // Leer UID
#   String tag = "";
#   for (byte i = 0; i < mfrc522.uid.size; i++) {
#     tag += String(mfrc522.uid.uidByte[i], HEX);
#   }
#   tag.toUpperCase();

#   Serial.println("Tag detectado: " + tag);

#   // Enviar al servidor
#   if (WiFi.status() == WL_CONNECTED) {
#     HTTPClient http;
#     http.begin(server);
#     http.addHeader("Content-Type", "application/x-www-form-urlencoded");

#     String postData = "tag_uid=" + tag + "&device_id=ESP32_01";
#     int httpResponseCode = http.POST(postData);

#     if (httpResponseCode == 200) {
#       String response = http.getString();
#       Serial.println("Respuesta servidor: " + response);

#       if (response.indexOf("OK") >= 0) {
#         accesoPermitido();
#       } else {
#         accesoDenegado();
#       }
#     } else {
#       Serial.println("Error en request: " + String(httpResponseCode));
#     }

#     http.end();
#   }

#   delay(2000);
# }

# void accesoPermitido() {
#   lcd.clear();
#   lcd.print("Tarjeta OK");
#   lcd.setCursor(0, 1);
#   lcd.print("Acceso Permitido");
#   digitalWrite(m1, HIGH);
#   digitalWrite(greenLed, HIGH);
#   delay(2000);
#   digitalWrite(m1, LOW);
#   digitalWrite(greenLed, LOW);
#   initialMessage();
# }

# void accesoDenegado() {
#   lcd.clear();
#   lcd.print("Tarjeta invalida");
#   digitalWrite(redLed, HIGH);
#   delay(2000);
#   digitalWrite(redLed, LOW);
#   initialMessage();
# }

# void initialMessage() {
#   lcd.clear();
#   lcd.print(" Acerca tu");
#   lcd.setCursor(0, 1);
#   lcd.print(" Tarjeta o tag");
# }
