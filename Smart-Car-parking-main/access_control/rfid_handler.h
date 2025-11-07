#ifndef RFID_HANDLER_H
#define RFID_HANDLER_H

// Initializes the RFID reader.
void setupRfid();

// Checks for new cards, validates them with Google Sheets, and commands the gate.
// This function is non-blocking and safe to call in the main loop.
void handleRfid();

#endif