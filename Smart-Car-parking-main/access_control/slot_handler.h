#ifndef SLOT_HANDLER_H
#define SLOT_HANDLER_H

#include <Arduino.h>

// Initializes the sensor pins.
void setupSlots();

// Checks all sensors for state changes. Call this in the main loop.
void handleSlots();

// Returns a count of how many slots are currently free.
int getFreeSlotCount();

// Returns a formatted string listing the numbers of the free slots.
String getFreeSlotsString();

#endif