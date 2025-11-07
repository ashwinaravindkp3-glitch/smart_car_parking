#include "slot_handler.h"
#include "network_handler.h" // <-- Include this to call the publish function

// --- Configuration ---
// Note: NUM_REAL_SENSORS is now defined in network_handler.h
const int SENSOR_PINS[NUM_REAL_SENSORS] = {34, 35, 32, 33, 25, 26, 27};

// --- Module Variables ---
bool realSlotOccupied[NUM_REAL_SENSORS] = {false};

// in slot_handler.cpp

void setupSlots() {
  for (int i = 0; i < NUM_REAL_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
    // Read the initial state of the sensor to prevent a false trigger on the first loop
    realSlotOccupied[i] = (digitalRead(SENSOR_PINS[i]) == LOW);
  }
  Serial.println("Initial sensor states have been read.");
}

void handleSlots() {
  bool stateHasChanged = false;

  for (int i = 0; i < NUM_REAL_SENSORS; i++) {
    bool isOccupied = (digitalRead(SENSOR_PINS[i]) == LOW);
    if (isOccupied != realSlotOccupied[i]) {
      realSlotOccupied[i] = isOccupied;
      stateHasChanged = true;
    }
  }

  if (stateHasChanged) {
    Serial.println("Slot Handler: State change detected, calling network handler to publish.");
    // Call the function from the network handler, passing our current sensor states
    publishSlotStatus(realSlotOccupied);
  }
}