#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

#include "config.h"

// SD Card
const int SdChipSelect = D4;
File myFile;

// Stateful
bool isRecording = false;
bool isMotion = false;

// Thresholds
double accelerationZeroThreshold = 3;
int wifiTimeout = 10;
int serialBaud = 115200;

Adafruit_MPU6050 mpu;
HTTPClient http;
WiFiClient client;
ESP8266WebServer webserver(80);

/** SETUP **/
bool setupWifi() {
  WiFi.hostname(getDeviceUID());
  WiFi.begin(WIFI_SSID, WIFI_PASS); 

  Serial.print("WiFi Connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  return true;
}

void setupBuzzer() {
  pinMode(BUZZER, OUTPUT);
}

bool setupSD() {
  Serial.print("Initializing SD card... ");

  if (!SD.begin(SdChipSelect)) {
    Serial.println("initialization failed!");
    return false;
  }

  Serial.println("initialization done.");
  return true;
}

void readSD() {
  char* path = "/httpdocs/index.html";
  myFile = SD.open(path);
  if (myFile) {
    Serial.println(path);

    // read from the file until there's nothing else in it:
    while (myFile.available()) {
      Serial.write(myFile.read());
    }
    // close the file:
    myFile.close();

  } else {
    // if the file didn't open, print an error:
    Serial.print("error opening ");
    Serial.println(path);
  }
}

String getDeviceUID() {
  return "TIMECUBE-" + String(ESP.getChipId());
}

// TODO Shake detection for start/top
//      Buzzer to indicate start/stop

// TODO Basic Web Server for device info & setup instructions

// TODO Log to SD card

// TODO Real Time Clock?

void blink(uint8_t Pin, int Count, int Duration) {
  for (int i = 0; i < Count; i++) {
    digitalWrite(Pin, HIGH); 
    delay(Duration/2);
    digitalWrite(BUZZER, LOW);
    delay(Duration/2);
  }
}

void motionDetected() {
  Serial.print("Motion Detected... ");
  int timeout = 10;

  if (isRecording) {
    Serial.println("Stopping Recording");
    blink(BUZZER, 2, 150);
  } else {
    Serial.println("Starting Recording");
    blink(BUZZER, 1, 150);
  }
  isRecording = !isRecording;

  // Work out Direction
  sensors_event_t a, g, temp;
  String direction = "";

  while (direction == "" && timeout > 0) {
    delay(100);
    timeout--;

    mpu.getEvent(&a, &g, &temp);
    direction = getFace(a.acceleration.x, a.acceleration.y, a.acceleration.z);
  }

  if (direction == "") {
    Serial.println("Failed to detect direction after motion");
    blink(BUZZER, 1, 500);
    return;
  }

  Serial.print("Direction: ");
  Serial.println(direction);
}

void setup() {
  Serial.begin(serialBaud);

  // Init Gyro
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    return;
  }
  Serial.println("MPU6050 Found!");

  //setupt motion detection
  mpu.setHighPassFilter(MPU6050_HIGHPASS_0_63_HZ);
  mpu.setMotionDetectionThreshold(30);
  mpu.setMotionDetectionDuration(80);
  mpu.setInterruptPinLatch(false);	// Keep it latched.  Will turn off when reinitialized.
  mpu.setInterruptPinPolarity(true);
  mpu.setMotionInterrupt(true);

  // Setup Wifi
  if (!setupWifi()) {
    Serial.println("Failed to setup wifi");
    return;
  }
  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());

  // Setup SD Card
  if (!setupSD()) {
    Serial.println("Failed to setup SD Card");
    return;
  }
  readSD();

  // Setup Device ID
  Serial.print("Device UUID: ");
  Serial.println(getDeviceUID());

  // Setup Buzzer
  setupBuzzer();

  // Reset Recording State
  isRecording = false;
  isMotion = false;

  // Start Web Server
  webserver.on("/", httpIndex);
  webserver.begin();
}

void loop() {
  /* Listen for Web Requests */
  webserver.handleClient(); 

  /* Look for Motion */
  if(mpu.getMotionInterruptStatus()) {
    /* Get new sensor events with the readings */
    motionDetected();

    // /* Print out the values */
    // Serial.print("Acceleration X: ");
    // Serial.print(a.acceleration.x);
    // Serial.print(", Y: ");
    // Serial.print(a.acceleration.y);
    // Serial.print(", Z: ");
    // Serial.print(a.acceleration.z);
    // Serial.println(" m/s^2");

    

    Serial.println("");
  }

  delay(100);
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
