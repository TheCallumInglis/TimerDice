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

char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

// TODO Log to SD card
// TODO Real Time Clock?

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

void setupBuzzer() {
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);
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

  Serial.println("[RTC] :: Setting the time now...");
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

  Serial.println("Init done.");
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
  
  setupBuzzer(); // Setup Buzzer (Shut the thing up if pin is HIGH on boot)

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

void blink(uint8_t Pin, int Count, int Duration) {
  for (int i = 0; i < Count; i++) {
    digitalWrite(Pin, HIGH); 
    delay(Duration/2);
    digitalWrite(BUZZER, LOW);
    delay(Duration/2);
  }
}

void motionDetected() {
  if (isMotion || slack > 0) { return; }

  Serial.print("[MOTION] Motion Detected... ");
  isMotion = true;
  slack = SLACK;

  if (isRecording) {
    Serial.println("Stopping Recording");
    blink(BUZZER, 2, 150);
    // TODO Handle Stop Recording
    
  } else {
    Serial.println("Starting Recording");
    blink(BUZZER, 1, 300);
    handleRecordingStart();
  }

  isRecording = !isRecording;
  isMotion = false;
  delay(250);
}

void handleRecordingStart() {
  String direction = "";
  sensors_event_t a, g, temp;

  // Poll for direction until found or timeout reached
  Serial.print("[MOTION] Detecting Direction...");
  while (direction == "" && searchDirectionTimeout > 0) {
    mpu.getEvent(&a, &g, &temp);
    direction = getFace(a.acceleration.x, a.acceleration.y, a.acceleration.z);

    delay(SEARCH_DIRECTION_INTERVAL);
    searchDirectionTimeout--;
    Serial.print(".");
  }

  // /* Print out the values */
  // Serial.print("Acceleration X: ");
  // Serial.print(a.acceleration.x);
  // Serial.print(", Y: ");
  // Serial.print(a.acceleration.y);
  // Serial.print(", Z: ");
  // Serial.print(a.acceleration.z);
  // Serial.println(" m/s^2");

  if (direction == "") {
    Serial.println("Failed to detect direction after motion");
    blink(BUZZER, 1, 2000);

    isRecording = false;
    isMotion = false;
    slack = 0;
    return;
  }
  
  Serial.println(direction);

  // TODO Log Start
  logStartRecording(direction);
}

bool logStartRecording(String face) {
  File dataFile = SD.open(RECORDING_FILE, FILE_WRITE);

  if (!dataFile) { 
    Serial.print("[logStartRecording] Error opening");
    Serial.println(RECORDING_FILE);
    return false;
  }

  String dataString = ""; // UID,FACE,START,END
  dataString += getDeviceUID(); dataString += ","; // Device UID
  dataString += face; dataString += ","; // Face
  dataString += getDateTimeNow(); dataString += ","; // Start Time
  dataString += "null"; // End Time = null

  dataFile.println(dataString);
  dataFile.close();
  Serial.println(dataString);

  return true;
}

bool logStopRecording() {
  File dataFile = SD.open(RECORDING_FILE, FILE_READ);

  if (!dataFile) { 
    Serial.print("[logStartRecording] Error opening");
    Serial.println(RECORDING_FILE);
    return false;
  }

  // TODO Close Recording Line
  return true;
}

void loop() {
  /* Look for Motion */
  if(mpu.getMotionInterruptStatus()) {
    motionDetected();
  }

  delay(100);
  slack = max(slack - 1, 0); // Slack acts like debounce to prevent multiple motion fire events from same motion.
}

/**
 * Returns true when value can be considered 0
 */
bool zeroThreshold(double val) {
  double absVal = fabs(val);
  return (absVal >= 0 && absVal <= ACCELERATION_ZERO_THRESHOLD);
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
