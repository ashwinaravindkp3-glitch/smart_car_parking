#ifndef NETWORK_HANDLER_H
#define NETWORK_HANDLER_H

// The number of real sensors we have connected.
// We define it here so both handlers can see it.
const int NUM_REAL_SENSORS = 7;

void setupNetwork();
void networkLoop();

// This is our new function for publishing the full slot status.
// It takes an array of boolean states from the slot_handler.
void publishSlotStatus(const bool realSlotStates[NUM_REAL_SENSORS]);

#endif