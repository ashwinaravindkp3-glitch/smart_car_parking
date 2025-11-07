// -----------------------------------------------------------------------------
// Main sketch for the Smart Car Parking Access Control System
// This file contains the primary setup and loop functions.
// It acts as the orchestrator for the different modules.
// -----------------------------------------------------------------------------

#include <WiFi.h>

// Include our custom modules. We will create these files next.
#include "rfid_handler.h"
#include "gate_handler.h"
#include "system_state.h"
#include "slot_handler.h"

// --- Global System Configuration ---
const char* WIFI_SSID = "Vraddd's s24+";
const char* WIFI_PASSWORD = "00000000";
String GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyRcDtN5GZJNZLhHhud2-y1SFkVKnksgVBEqPpy3og8myL6VQOumz0wz_iZxcMJ-ed7EQ/exec";



bool userJustValidated = false;
// -----------------------------------------------------------------------------
// SETUP: Runs once on boot.
// -----------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  Serial.println("Booting Access Control System...");

  // Initialize modules one by one
  setupWifi();
  setupRfid();
  setupGate();
  setupSlots();

  Serial.println("System Initialized. Ready.");
}

// -----------------------------------------------------------------------------
// LOOP: Runs continuously.
// This is the core of our non-blocking system. Each handler function
// will be designed to run quickly and not use delay().
// -----------------------------------------------------------------------------
void loop() {
  handleRfid(); // Checks for new cards and handles validation
  handleGate(); // Checks the gate timer and closes the gate if needed
  handleSlots();
}


// -----------------------------------------------------------------------------
// Helper function to connect to WiFi.
// We can move this to a "network_handler.cpp" file later to be even cleaner.
// -----------------------------------------------------------------------------
void setupWifi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected.");
}