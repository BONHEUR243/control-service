#include <Wire.h>
#include <ESP8266WiFi.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <MFRC522.h>
#include <time.h>

#define SS_PIN 2
#define RST_PIN 0

MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);
const char* serverName = "http://192.168.43.92:8000/check_rfid/"; 

void setup() {
  Serial.begin(115200);
  SPI.begin();
  rfid.PCD_Init();
  lcd.init();
  lcd.backlight();

  WiFi.begin("Armand", "mecanique");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Wifi connected!");

  // Configurer le fuseau horaire
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  setenv("TZ", "CAT-2", 1); // Fuseau horaire de l'Afrique centrale
  tzset();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Placez la carte!");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }

  String cardId = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    cardId += String(rfid.uid.uidByte[i]<0x10? "0":"");
    cardId += String(rfid.uid.uidByte[i], HEX);
  }
  cardId.toUpperCase();
  
  //lcd.clear();
  //lcd.setCursor(0, 0);
  //lcd.print("Card ID:");
  //lcd.setCursor(0, 1);
  //lcd.print(cardId);
  Serial.println(cardId);

  //delay(1000);

      if (WiFi.status() == WL_CONNECTED) {
        WiFiClient client;
        HTTPClient http;
        Serial.println("Sending HTTP request..."); // Message de débogage

        http.begin(client, serverName); // Utiliser la nouvelle signature de begin
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");
        String postData = "cardId=" + cardId;

        int httpResponseCode = http.POST(postData);

        if (httpResponseCode > 0) {
          String response = http.getString();
          Serial.println(httpResponseCode);
          Serial.println(response);

          DynamicJsonDocument doc(1024);
          deserializeJson(doc, response);

          const char* status = doc["status"];
          const char* message = doc["message"];
          const char* name = doc["student_name"];

          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print(status);
          lcd.setCursor(0, 1);
          lcd.print(name);

          if (strcmp(status, "authorized") == 0) {
            digitalWrite(LED_BUILTIN, LOW); // Lampe verte allumée
            Serial.println("allowed");
            //lcd.clear();
            //lcd.setCursor(0, 0);
            //lcd.print("allowed");

          } else {
            digitalWrite(LED_BUILTIN, HIGH); // Lampe rouge allumée
            Serial.println("not allowed");
            //lcd.clear();
            //lcd.setCursor(0, 0);
            //lcd.print("not allowed");
          }

        } else {
          Serial.print("Error on sending POST: ");
          Serial.println(httpResponseCode);
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Error...");
        }

        http.end();
      } else {
        Serial.println("WiFi not connected");
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Connexion lost!");
      }

      delay(3000);
}