#include "gate_handler.h"
#include "slot_handler.h"
#include "network_handler.h"



void setup() {
  Serial.begin(115200);
  Serial.println("Booting Smart Parking System...");

  setupNetwork();
  setupGate();
  setupSlots();

  Serial.println("System Initialized. Ready.");
}

void loop() {
  delay(10);
  networkLoop(); 
  handleGate();  
  handleSlots(); 
}