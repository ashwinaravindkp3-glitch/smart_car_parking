#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "network_handler.h"
#include "gate_handler.h"

// --- Configuration ---
const char* WIFI_SSID = "thegooddoctor62";
const char* WIFI_PASSWORD = "qzju6234";
const char* MQTT_BROKER = "344221df652946139079042b380d50c9.s1.eu.hivemq.cloud";
const int MQTT_PORT = 8883;
const char* MQTT_USER = "thegooddoctor62";
const char* MQTT_PASSWORD = "Ashwin@25";

// --- Topics ---
const char* MQTT_SUBSCRIBE_TOPIC = "door_open";
const char* MQTT_PUBLISH_TOPIC_SLOTS = "parking/esp32/status";

// --- Slot Mapping ---
const int TOTAL_SLOTS = 20;
const int REAL_SLOT_MAPPING[NUM_REAL_SENSORS] = {2, 5, 6, 9, 13, 17, 19};

// --- Global Clients ---
WiFiClientSecure wifiClientSecure;
PubSubClient mqttClient(wifiClientSecure);
unsigned long lastReconnectAttempt = 0;

// --- Forward Declarations ---
void reconnectMqtt();
void mqttCallback(char* topic, byte* payload, unsigned int length); // <-- FIX: Added forward declaration

// --- Callback Function (Handles incoming messages) ---
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.printf("Message Received! Topic: %s, Payload: %s\n", topic, message.c_str());

  if (strcmp(topic, MQTT_SUBSCRIBE_TOPIC) == 0) {
    if (message.equalsIgnoreCase("OPEN")) {
      Serial.println("Network Handler: OPEN command received. Triggering gate.");
      openGate();
    } else {
      Serial.println("Network Handler: Unknown command received.");
    }
  }
}

// --- Setup Function ---
void setupNetwork() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected.");

  wifiClientSecure.setInsecure();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
}

// --- Main Loop Function ---
void networkLoop() {
  if (!mqttClient.connected()) {
    reconnectMqtt();
  }
  mqttClient.loop();
}

// --- Reconnect Function (Only one copy now) ---
void reconnectMqtt() {
    long now = millis();
    if (now - lastReconnectAttempt > 5000) {
        lastReconnectAttempt = now;
        if (!mqttClient.connected()) {
            Serial.print("Attempting MQTT connection...");
            String clientId = "ESP32-Parking-Client-";
            clientId += String(random(0xffff), HEX);
            
            if (mqttClient.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
                Serial.println("connected!");
                mqttClient.subscribe(MQTT_SUBSCRIBE_TOPIC);
                Serial.printf("Subscribed to: %s\n", MQTT_SUBSCRIBE_TOPIC);
            } else {
                Serial.printf("failed, rc=%d try again in 5 seconds\n", mqttClient.state());
            }
        }
    }
}

// --- Publish Function ---
void publishSlotStatus(const bool realSlotStates[NUM_REAL_SENSORS]) {
  Serial.println("-> Entered publishSlotStatus function.");
  if (!mqttClient.connected()) {
    Serial.println("   [DEBUG] MQTT client not connected. Aborting publish.");
    return;
  }

  StaticJsonDocument<1024> doc;
  JsonArray slotsArray = doc.createNestedArray("slots");

  for (int i = 0; i < TOTAL_SLOTS; i++) {
    int currentSlotNumber = i + 1;
    JsonObject slotObject = slotsArray.createNestedObject();
    slotObject["slotNumber"] = currentSlotNumber;

    int sensorIndex = -1;
    for (int j = 0; j < NUM_REAL_SENSORS; j++) {
      if (REAL_SLOT_MAPPING[j] == currentSlotNumber) {
        sensorIndex = j;
        break;
      }
    }

    if (sensorIndex != -1) {
      slotObject["status"] = realSlotStates[sensorIndex] ? "occupied" : "available";
    } else {
      slotObject["status"] = "occupied";
    }
  }

  char jsonBuffer[1024];
  serializeJson(doc, jsonBuffer);

  Serial.println("   [DEBUG] JSON payload created successfully. Contents:");
  Serial.println(jsonBuffer);
  Serial.printf("   [DEBUG] Publishing to topic: %s\n", MQTT_PUBLISH_TOPIC_SLOTS);
  mqttClient.publish(MQTT_PUBLISH_TOPIC_SLOTS, "test");
  mqttClient.publish(MQTT_PUBLISH_TOPIC_SLOTS, jsonBuffer);
  Serial.println("<- Exiting publishSlotStatus function.");
}