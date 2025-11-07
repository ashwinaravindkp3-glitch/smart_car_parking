#include <Arduino.h>
#include <ESP32Servo.h>
#include "gate_handler.h"

// --- Pin Definitions ---
#define SERVO_PIN 2

// --- Constants ---
const long GATE_OPEN_DURATION = 5000; // Keep gate open for 5 seconds
const int GATE_CLOSED_ANGLE = 0;
const int GATE_OPEN_ANGLE = 90;

// --- Module-specific (static) Variables ---
static Servo gateServo;
static unsigned long gateOpenTimer = 0;
static bool isGateOpen = false;

// Initializes the servo motor.
void setupGate() {
  gateServo.attach(SERVO_PIN);
  gateServo.write(GATE_CLOSED_ANGLE); // Ensure gate is closed on startup
}

// Opens the gate and starts the non-blocking timer.
void openGate() {
  Serial.println("Gate Handler: Opening gate.");
  gateServo.write(GATE_OPEN_ANGLE);
  isGateOpen = true;
  gateOpenTimer = millis(); // Start the timer!
}

// This function is called continuously from the main loop().
void handleGate() {
  // If the gate isn't open, there's nothing to do.
  if (!isGateOpen) {
    return;
  }

  // Check if the timer has expired.
  if (millis() - gateOpenTimer > GATE_OPEN_DURATION) {
    Serial.println("Gate Handler: Timer expired. Closing gate.");
    gateServo.write(GATE_CLOSED_ANGLE);
    isGateOpen = false;
  }
}