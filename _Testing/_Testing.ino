#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

#include "config.h"

// Device & Server Config
const char* UUID = ""; // Auto-filled from MAC Address during setup()

// Stateful
bool isRecording = false;

// Thresholds
double accelerationZeroThreshold = 3;
int wifiTimeout = 10;
int serialBaud = 115200;

Adafruit_MPU6050 mpu;
HTTPClient http;

/** SETUP **/
bool setupWifi() {
  WiFi.config();
  WiFi.begin(WIFI_SSID, WIFI_PASS); 

  while (WiFi.status() != WL_CONNECTED && wifiTimeout > 0) {
    Serial.println("Waiting for connection");
    delay(5000);
    
    wifiTimeout--;
  }

  return WiFi.status() != WL_CONNECTED;
}

String getDeviceUID() {
  return String(ESP.getChipId());
}

// TODO Shake detection for start/top
//      Buzzer to indicate start/stop

// TODO Post to Web API

// TODO Basic Web Server for device info & setup instructions

// TODO Log to SD card

// TODO Real Time Clock?

void setup() {
  Serial.begin(serialBaud);

  // Init Gyro
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    return;
  }
  Serial.println("MPU6050 Found!");

  // Setup Wifi
  if (!setupWifi()) {
    Serial.println("Failed to setup wifi");
    return;
  }
  Serial.println("WIFI Connected!");

  // Setup Device ID
  UUID = getDeviceUID();
  Serial.print("Device UUID: ");
  Serial.println(UUID);

  // Reset Recording State
  isRecording = false;
}

void loop() {
  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  /* Print out the values */
  Serial.print("Acceleration X: ");
  Serial.print(a.acceleration.x);
  Serial.print(", Y: ");
  Serial.print(a.acceleration.y);
  Serial.print(", Z: ");
  Serial.print(a.acceleration.z);
  Serial.println(" m/s^2");


  Serial.print("Direction: ");
  Serial.println(getFace(a.acceleration.x, a.acceleration.y, a.acceleration.z));

  Serial.println("");
  delay(1500);
}

/**
 * Returns true when value can be considered 0
 */
bool zeroThreshold(double val) {
  double absVal = fabs(val);
  return (absVal >= 0 && absVal <= accelerationZeroThreshold);
}

String getFace(double x, double y, double z) {
  String face;
  // 6-Sides

  //                X.    Y.    Z. 
  // Up             0     0     10      Z
  // Upsidedown     0     0     -10

  // Left           10    0     0       X
  // Right          -10   0     0

  // Nose           0     -10   0       Y
  // Tail           0     10    0

  // Z
  if (zeroThreshold(x) && zeroThreshold(y)) {
    if (z > 0) {
      face = "Up";
    } else {
      face = "Upsidedown";
    }
  }

  // X
  if (zeroThreshold(y) && zeroThreshold(z)) {
    if (x > 0) {
      face = "left";
    } else {
      face = "right";
    }
  }

  // Y
  if (zeroThreshold(x) && zeroThreshold(z)) {
    if (y > 0) {
      face = "tail";
    } else {
      face = "nose";
    }
  }

  return face;
}

void startRecordingTask(String faceName) {
  http.begin(API);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  http.addHeader("APIKEY", APIKEY);

  String postData = "DiceUUID=" + UUID + "&FaceName=" + faceName;

  int httpCode = http.POST(postData);
  String payload = http.getString();

  Serial.println(postData);
  Serial.println(httpCode);
  Serial.println(payload);

  http.end();
}

void stopRecordingTask() {
  // TODO
}