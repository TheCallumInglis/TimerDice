#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <stdio.h>
#include <math.h>
#include <SPI.h>
#include <SD.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

#include "config.h"
#include "functions.h"
#include "time.h"
#include "sd.h"
#include "dice.h"
#include "mqtt.h"
#include "recording.h"

// Stateful
int face_switch_counter = 0;
int slack = 0;

// SD Card
const int SdChipSelect = A0;

// Instance
HTTPClient http;
ESP8266WebServer webserver(80);

/** SETUP :: Start **/
bool setupWifi() {
  WiFi.hostname(GetDeviceUID());
  WiFi.begin(WIFI_SSID, WIFI_PASS); 

  Serial.print("[WiFi] :: Connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  // WiFi 
  Serial.print("[WiFi] :: Connected, IP address: ");
  Serial.println(WiFi.localIP());

  return true;
}

void setupIndicators() {
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);

  pinMode(RECORDING_INDICATOR, OUTPUT);
  digitalWrite(RECORDING_INDICATOR, LOW);
}

bool setupMPU() {
  Serial.println("[MPU6050] :: Connecting...!");

  if (!mpu.begin(GRYO_I2C)) {
    Serial.println("[MPU6050] :: Failed to find MPU6050 chip");
    return false;
  }
  Serial.println("[MPU6050] :: Found!");

  // Setup motion detection
  mpu.setHighPassFilter(MPU6050_HIGHPASS_0_63_HZ);
  mpu.setMotionDetectionThreshold(MOTION_DETECTION_THRESHOLD);
  mpu.setMotionDetectionDuration(MOTION_DETECTION_DURATION);
  mpu.setInterruptPinLatch(false);	// Keep it latched.  Will turn off when reinitialized.
  mpu.setInterruptPinPolarity(true);
  mpu.setMotionInterrupt(true);

  Serial.println("[MPU6050] :: Configured!");
  return true;
}

bool setupSD() {
  Serial.print("[SD Card] Initializing SD card... ");

  if (!SD.begin(SdChipSelect)) {
    Serial.println("Init failed!");
    return false;
  }

  // Check Directories Exist
  if (!SD.exists(RECORDING_DIR)) {
    Serial.print("RECORDING_DIR does not exist... will try and create directory ");
    Serial.print(RECORDING_DIR);

    // Try create it
    if (!SD.mkdir(RECORDING_DIR)) {
      Serial.print(" Failed to create directory!");
      return false;
    }
    Serial.println(" Directory Created!");
  }

  Serial.println("[SD Card] Init done.");
  return true;
}

void setupWebServer() {
  Serial.println("[webserver] :: Starting...");

  webserver.on("/", httpIndex);
  webserver.begin();

  Serial.println("[webserver] :: Started");
}

void setupNeopixel() {
  FastLED.addLeds<LED_TYPE, LED_PIN, LED_COLOUR_ORDER>(leds, LED_COUNT);
  Serial.println("[Neopixel] Init done.");

  delay(200);
  ClearDiceColour();
}

void setupNotice() {
  // Device ID
  Serial.print("[NOTICE] :: Device UUID: ");
  Serial.println(GetDeviceUID());

  // Search Duration Timeout
  Serial.print("[NOTICE] :: We will make ");
  Serial.print(SEARCH_DIRECTION_THRESHOLD * 1000 / SEARCH_DIRECTION_INTERVAL);
  Serial.println(" attempts to determine direction/orientation after recording start.");

  // Ready To Go
  blink(BUZZER, 2, 100);
  Serial.println();
}

void setup() {
  delay(3000);
  Serial.begin(SERIAL_BAUD);
  
  setupIndicators(); // Setup Buzzer & other outputs (Shut the thing up if buzzin' on boot)

  // Setup MPU6050 (Gyro)
  if (!setupMPU()) {
    Serial.println("[ERROR] :: Failed to setup MPU6050");
    return;
  }

  // Setup Wifi
  if (!setupWifi()) {
    Serial.println("[ERROR] :: Failed to setup wifi");
    return;
  }

  if (!setupSD()) {
    Serial.println("[ERROR] :: Failed to setup SD Card");
    return;
  }

  // Setup RTC
  if (!SetupRTC()) {
    Serial.println("[ERROR] :: Failed to setup RTC");
    return;
  }

  // Setup MQTT
  mqttClient.setServer(MQTT_URL, 1883);

  // Setup Neopixel
  setupNeopixel();

  srand(rtc.now().unixtime()); // Seed Random
  SetupRecording();
  setupWebServer(); // Setup Web Server
  setupNotice(); // Ready to Go
}
/** SETUP :: End **/

void motionDetected() {
  if (is_motion || slack > 0) { return; }

  Serial.print("[MOTION] Motion Detected... ");
  is_motion = true;
  slack = SLACK;

  if (is_recording) {
    StopRecording();
    
  } else {
    if (!StartRecording()) {
      slack = 0;
    }
  }

  is_motion = false;
  delay(250);
}

void loop() {
  /* Look for Motion */
  if(mpu.getMotionInterruptStatus()) {
    motionDetected();
  }

  /* Check current face matches what we're recording */
  int current_face = GetDiceFaceNow();
  if (is_recording && current_face != 0 && current_face != face_recording) {
    face_switch_counter++;

    // Wait a bit, check this is sensible
    if (face_switch_counter > (FACE_SWITCH_THRESHOLD * 1000) / LOOP_DELAY) {
      Serial.println("Detect face switch! Moving to new face");
      Serial.print("Old Face: "); Serial.println(face_recording);
      Serial.print("New Face: "); Serial.println(current_face);

      // Stop current recording & start new
      if (!StopRecording()) {
        blink(BUZZER, 5, 200);
      }

      if (!StartRecording()) {
        blink(BUZZER, 5, 200);
      }

      // TODO Handle checking that this worked

      face_switch_counter = 0;
    }
  }

  webserver.handleClient(); // Listen for Web Requests

  /* Recording in progress */
  //digitalWrite(RECORDING_INDICATOR, (isRecording ? HIGH : LOW)); 

  delay(LOOP_DELAY);
  slack = max(slack - 1, 0); // Slack acts like debounce to prevent multiple motion fire events from same motion.
}

/** HTTP Server **/
void httpIndex() { 
  String page = "";

  page += "<html>";
  page +=   "<head>";
  page +=     "<title>"; page += GetDeviceUID(); page += "</title>"; 
  page +=     "<style> body {color: #dee2e6;background-color: #212529;margin: 5%;font-family: Arial, Helvetica, sans-serif;}h1 {text-align: center;font-size: 2em;margin: 5% auto 2%;}table {border-collapse: collapse;min-width: 60%;margin: auto;}table td, table th {border: 1px solid #495057;padding: 8px;}table tr td:nth-child(1){font-weight: bold;}table tr.bold-border-top {border-top: 2px solid;}</style>";
  page +=   "</head>";
  page +=   "<body>";
  page +=     "<h1>Timer Cube</h1>";
  page +=     "<table><tbody>";
  page +=     "<tr><td>Device UUID</td><td>"; page += GetDeviceUID(); page += "</td></tr>";
  page +=     "<tr><td>API Key</td><td>"; page += APIKEY; page += "</td></tr>";

  page +=     "<tr class='bold-border-top'><td>WiFi Network</td><td>"; page += WIFI_SSID; page += "</td></tr>";
  page +=     "<tr><td>IP Address</td><td>"; page += WiFi.localIP().toString().c_str(); page += "</td></tr>";

  page +=     "<tr class='bold-border-top'><td>MQTT Server</td><td>"; page += MQTT_URL; page += "</td></tr>";
  page +=     "<tr><td>MQTT User</td><td>"; page += MQTT_USER; page += "</td></tr>";

  page +=     "<tr class='bold-border-top'><td>NTP Server</td><td>"; page += NTPServer; page += "</td></tr>";
  page +=     "<tr><td>Current Time</td><td>"; page += GetDateTimeNow(); page += "</td></tr>";

  page +=     "<tr class='bold-border-top'><td>Number of Faces</td><td>"; page += DICE_FACES; page += "</td></tr>";
  page +=     "<tr><td>Face Switch Threshold </td><td>"; page += FACE_SWITCH_THRESHOLD; page += " seconds</td></tr>";
  page +=     "<tr><td>Recording Path</td><td>"; page += RECORDING_DIR; page += "</td></tr>";
  page +=     "</tbody></table>";
  page +=   "</body>";
  page += "</html>";

  webserver.send(200, "text/html", page); 
}
