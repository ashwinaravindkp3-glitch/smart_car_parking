#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

#include "rfid_handler.h"
#include "gate_handler.h" // We need to include this to call openGate()
#include "system_state.h"
// --- Pin Definitions ---
#define SS_PIN    5 
#define RST_PIN   21

// --- Module-specific (static) Variables ---
static MFRC522 mfrc522(SS_PIN, RST_PIN);
static HTTPClient http;

// This tells the compiler that this variable exists, but it's defined
// in another file (our main AccessControl.ino). This is how we share it.
extern String GOOGLE_SCRIPT_URL;

// Initializes the RFID reader hardware.
void setupRfid() {
  SPI.begin();
  mfrc522.PCD_Init();
}

// This function is called continuously from the main loop().
void handleRfid() {
  // Look for a new card
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return; // No card present, so just exit the function.
  }

  // --- A card has been detected, process it ---
  String scannedUID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    scannedUID += String(mfrc522.uid.uidByte[i], HEX);
  }
  scannedUID.toUpperCase();
  Serial.print("RFID Handler: Card scanned, UID: ");
  Serial.println(scannedUID);

  // Send the UID to Google Sheets for validation
  String url = GOOGLE_SCRIPT_URL + "?uid=" + scannedUID;
  http.begin(url);
  http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
  
  int httpCode = http.GET();
  
  if (httpCode > 0 && (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY)) {
    String payload = http.getString();
    Serial.print("RFID Handler: Response from server: ");
    Serial.println(payload);

    if (payload == "yes") {
      // Validation successful! Tell the gate handler to open the gate.
            Serial.println("RFID Handler: Access Granted.");
      userJustValidated = true; // <-- Set the flag for the other module
      openGate();
    } else {
      Serial.println("RFID Handler: Access Denied.");
    }
  } else {
    Serial.printf("RFID Handler: HTTP request failed, error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
  mfrc522.PICC_HaltA();
}