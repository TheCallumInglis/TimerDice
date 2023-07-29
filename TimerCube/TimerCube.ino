#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <stdio.h>
#include <math.h>
#include <SPI.h>
#include <SD.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include "RTClib.h"

#include "config.h"

// Stateful
bool isRecording = false;
int recordingID;
char recordingFile[32];

int recordingFace;
int currentFace;

int faceSwitchCounter = 0;
int faceSwitchThreshold = 5; // Seconds
bool isMotion = false;
int slack = 0;

// Thresholds
int searchDirectionTimeout = SEARCH_DIRECTION_THRESHOLD * 1000 / SEARCH_DIRECTION_INTERVAL;

// SD Card
const int SdChipSelect = D4;
File myFile;

// Instance
Adafruit_MPU6050 mpu;
HTTPClient http;
WiFiClient client;
ESP8266WebServer webserver(80);
RTC_DS1307 rtc;

/** SETUP :: Start **/
bool setupWifi() {
  WiFi.hostname(getDeviceUID());
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

bool setupRTC() {
  Serial.print("[RTC] :: Init...");

  if (!rtc.begin()) {
    Serial.println("Failed");
    return false;
  }
  Serial.println("Found!");

  Serial.println("[RTC] :: Setting the time now..."); // TODO Set to current time (NTP?)
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  Serial.println("[RTC] :: Time has been set");

  DateTime now = rtc.now();
  Serial.print("[RTC] :: The Time is Now: ");
  Serial.println(getDateTimeNow());

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

  webserver.handleClient(); // Listen for Web Requests

  Serial.println("[webserver] :: Started");
}

void setupInitVars() {
  // Reset Recording State
  isRecording = false;
  isMotion = false;  

  // Seed Random
  srand(rtc.now().unixtime());
}

void setupNotice() {
  // Device ID
  Serial.print("[NOTICE] :: Device UUID: ");
  Serial.println(getDeviceUID());

  // Search Duration Timeout
  Serial.print("[NOTICE] :: We will make ");
  Serial.print(searchDirectionTimeout);
  Serial.println(" attempts to determine direction/orientation after recording start.");

  // Ready To Go
  blink(BUZZER, 2, 100);
  Serial.println();
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  
  setupIndicators(); // Setup Buzzer & other outputs (Shut the thing up if pin is HIGH on boot)

  // Setup MPU6050 (Gyro)1
  if (!setupMPU()) {
    Serial.println("[ERROR] :: Failed to setup MPU6050");
    return;
  }

  // Setup RTC
  if (!setupRTC()) {
    Serial.println("[ERROR] :: Failed to setup RTC");
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

  setupWebServer(); // Setup Web Server
  setupInitVars(); // Initialise run-time vars
  setupNotice(); // Ready to Go
}
/** SETUP :: End **/


// void readSD() {
//   String path = "/httpdocs/index.html";
//   myFile = SD.open(path);
//   if (myFile) {
//     Serial.println(path);

//     // read from the file until there's nothing else in it:
//     while (myFile.available()) {
//       Serial.write(myFile.read());
//     }
//     // close the file:
//     myFile.close();

//   } else {
//     // if the file didn't open, print an error:
//     Serial.print("error opening ");
//     Serial.println(path);
//   }
// }

String getDeviceUID() {
  return "TIMECUBE-" + String(ESP.getChipId());
}

String getDateTimeNow() {
  DateTime now = rtc.now();
  char buffer[] = "YYYY-MM-DDThh:mm:ss";
  return now.toString(buffer);
}

int getRandomTaskID() {
  return rand() % 100000 + 10000; // 10,000 - 100,000
}

/**
 * Generate a unique recording file path
 * Within RECORDING_DIR:
 *    -> EPOCH-RAND.xml
 */
void getNewRecordingFilepath(char* outRecordingFile) {
  char epochBuffer[32]; // For epoch
  char idBuffer[6]; // For Recording ID
  char filepath[64]; // New filepath

  int epoch = rtc.now().unixtime();
  sprintf(epochBuffer, "%d", epoch);

  strcpy(filepath, "");

  // Find unique filepath
  while (strlen(filepath) == 0 || SD.exists(filepath)) {
    recordingID = getRandomTaskID();
    sprintf(idBuffer, "%d", recordingID);

    strcpy(filepath, RECORDING_DIR);
    strcat(filepath, epochBuffer);
    strcat(filepath, "-");
    strcat(filepath, idBuffer);
    strcat(filepath, ".xml");
  }

  strcpy(outRecordingFile, filepath);
}

void blink(uint8_t Pin, int Count, int Duration) {
  for (int i = 0; i < Count; i++) {
    digitalWrite(Pin, HIGH); 
    delay(Duration/2);
    digitalWrite(Pin, LOW);
    delay(Duration/2);
  }
}

void motionDetected() {
  if (isMotion || slack > 0) { return; }

  Serial.print("[MOTION] Motion Detected... ");
  isMotion = true;
  slack = SLACK;

  if (isRecording) {
    logStopRecording();
    
  } else {
    handleRecordingStart();
  }

  isMotion = false;
  delay(250);
}

bool handleRecordingStart() {
  Serial.println("Starting Recording");
  blink(BUZZER, 1, 300);
  delay(1000); // Allow time to position cube

  int face = -1;

  // Poll for direction until found or timeout reached
  Serial.print("[MOTION] Detecting Direction...");
  while (face == -1 && searchDirectionTimeout > 0) {
    face = getFaceNow();

    delay(SEARCH_DIRECTION_INTERVAL);
    searchDirectionTimeout--;
    Serial.print(".");
  }

  if (face == -1) {
    Serial.println("Failed to detect direction after motion");
    blink(BUZZER, 1, 2000);

    isRecording = false;
    isMotion = false;
    slack = 0;
    return false;
  }
  Serial.println(face);

  //  Log Start
  if(!logStartRecording(face)) {
    return false;
  }

  isRecording = true;
  recordingFace = face;
  return true;
}

/**
 * Write out recording logging to file
 */
bool logStartRecording(int face) {
  getNewRecordingFilepath(recordingFile);

  File dataFile = SD.open(recordingFile, FILE_WRITE);
  Serial.print("Recording File Path: "); Serial.println(recordingFile);

  if (!dataFile) { 
    Serial.print("[logStartRecording] Error opening");
    Serial.println(recordingFile);
    return false;
  }

  String dataString = "";
  dataString += "<deviceUID>"; dataString += getDeviceUID(); dataString += "</deviceUID>\r\n"; // Device UID
  dataString += "<recordingID>"; dataString += recordingID; dataString += "</recordingID>\r\n"; // Recording ID (Local)
  dataString += "<face>"; dataString += face; dataString += "</face>\r\n"; // Dice Face
  dataString += "<start>"; dataString += getDateTimeNow(); dataString += "</start>"; // Start Date/Time

  dataFile.println(dataString);
  dataFile.close();
  Serial.println(dataString);

  return true;
}

/**
 * Close of a recording file.. we expect the filepath to exist
 */
bool logStopRecording() {
  Serial.println("Stopping Recording");
  blink(BUZZER, 2, 150);
    
  if (!SD.exists(recordingFile)) {
    Serial.print("[logStartRecording] Error opening (File does not exist): ");
    Serial.println(recordingFile);
    return false;
    // TODO Maybe close off any "is recording" flags here...
  }

  File dataFile = SD.open(recordingFile, FILE_WRITE);

  if (!dataFile) { 
    Serial.print("[logStartRecording] Error opening");
    Serial.println(recordingFile);
    return false;
  }

  String dataString = "";
  dataString += "<end>"; dataString += getDateTimeNow(); dataString += "</end>"; // End Date/Time

  dataFile.println(dataString);
  dataFile.close();
  Serial.println(dataString);

  isRecording = false;
  return true;
}

void loop() {
  /* Look for Motion */
  if(mpu.getMotionInterruptStatus()) {
    motionDetected();
  }

  /* Check current face matches what we're recording */
  int currentFace = getFaceNow();
  if (isRecording && currentFace != -1 && currentFace != recordingFace) {
    faceSwitchCounter++;

    // Wait a bit, check this is sensible
    if (faceSwitchCounter > (faceSwitchThreshold * 1000) / LOOP_DELAY) {
      Serial.println("Detect face switch! Moving to new face");
      Serial.print("Old Face: "); Serial.println(recordingFace);
      Serial.print("New Face: "); Serial.println(currentFace);

      // Stop current recording
      if (logStopRecording()) {
        // Start new recording
        if (!handleRecordingStart()) {
          blink(BUZZER, 5, 200);
        }
      }

      // TODO Handle checking that this worked

      faceSwitchCounter = 0;
    }
  }

  /* Recording in progress */
  digitalWrite(RECORDING_INDICATOR, (isRecording ? HIGH : LOW)); 

  delay(LOOP_DELAY);
  slack = max(slack - 1, 0); // Slack acts like debounce to prevent multiple motion fire events from same motion.
}

bool fuzzyComp(double value, double threshold) {
  return (value >= (threshold - ACCELERATION_ZERO_THRESHOLD) && value <= (threshold + ACCELERATION_ZERO_THRESHOLD));
}

int getFaceNow() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  return currentFace = getFace(a.acceleration.x, a.acceleration.y, a.acceleration.z);
}

int getFace(double x, double y, double z) {
  // X
  if (fuzzyComp(x, -9.8)) { // X roughly -9.8
    if (y < 0) { return 6; } else { return 11; }
  }

  if (fuzzyComp(x, -4.5)) { // X roughly -4.5
    if (y < 0) { return 5; } else { return 7; }
  }
  
  if (fuzzyComp(x, 0.0)) { // X roughly 0
    if (fuzzyComp(y, -9.8)) {
      return 1;
    } else if (fuzzyComp(y, -4.5)) {
      return 2;
    } else if (fuzzyComp(y,  4.5)) {
      return 10;
    } else if (fuzzyComp(y,  9.0)) {
      return 12;
    }
  }

  if (fuzzyComp(x, 4.5)) { // X roughly 4.5
    if (y < 0) { return 4; } else { return 8; }
  }

  if (fuzzyComp(x, 9.8)) { // X roughly 9.8 
    if (y < 0) { return 3; } else { return 9; }
  }

  return -1; // We broke it!
}

void startRecordingTask(char* faceName) {
  http.begin(client, API + "recording/start");
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  http.addHeader("APIKEY", APIKEY);

  String postData = "DiceUUID=" + getDeviceUID() + "&FaceName=" + faceName;

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

/** HTTP Server **/
void httpIndex() { 
  webserver.send(200, "text/plain", "Hello World! Device UUID: " + getDeviceUID()); 
}
