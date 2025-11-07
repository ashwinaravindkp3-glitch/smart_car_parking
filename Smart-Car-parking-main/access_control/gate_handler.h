#ifndef GATE_HANDLER_H
#define GATE_HANDLER_H

// Initializes the servo motor and sets its starting position.
void setupGate();

// Opens the gate and starts the auto-close timer.
void openGate();

// Checks the timer and closes the gate if needed.
// This function is non-blocking and safe to call in the main loop.
void handleGate();

#endif