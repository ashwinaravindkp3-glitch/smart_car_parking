#include "slot_handler.h"
#include "system_state.h"
// The GPIO pins connected to the 8 IR sensors
const int SENSOR_PINS[8] = {34, 35, 32, 33, 25, 26, 27, 14};
const int NUM_SLOTS = 8;

// Array to hold the current state of each slot (true = occupied)
bool slotOccupied[NUM_SLOTS] = {false};

void setupSlots() {
  for (int i = 0; i < NUM_SLOTS; i++) {
    pinMode(SENSOR_PINS[i], INPUT);
  }
}

void handleSlots() {
  // This first part remains the same
  for (int i = 0; i < NUM_SLOTS; i++) {
    bool isOccupied = (digitalRead(SENSOR_PINS[i]) == LOW);
    if (isOccupied != slotOccupied[i]) {
      slotOccupied[i] = isOccupied;
      Serial.printf("Slot %d is now %s\n", i + 1, isOccupied ? "Occupied" : "Vacant");
    }
  }

  // --- NEW LOGIC ---
  // Check if a user was just validated by the RFID module.
  if (userJustValidated) {
    String freeSlotsMessage = getFreeSlotsString();
    Serial.println(freeSlotsMessage); // Print the message
    userJustValidated = false; // Reset the flag so we only print once
  }
}

int getFreeSlotCount() {
  int count = 0;
  for (int i = 0; i < NUM_SLOTS; i++) {
    if (!slotOccupied[i]) {
      count++;
    }
  }
  return count;
}

String getFreeSlotsString() {
  String freeSlots = "Available Slots: ";
  bool firstSlotFound = false;
  for (int i = 0; i < NUM_SLOTS; i++) {
    if (!slotOccupied[i]) {
      if (firstSlotFound) {
        freeSlots += ", ";
      }
      freeSlots += String(i + 1);
      firstSlotFound = true;
    }
  }
  if (!firstSlotFound) {
    return "Parking is full.";
  }
  return freeSlots;
}