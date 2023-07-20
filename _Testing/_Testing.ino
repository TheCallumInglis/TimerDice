#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

double accelerationZeroThreshold = 3;

void setup() {
  Serial.begin(115200);

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

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
  Serial.println(accelerationCalc(a.acceleration.x, a.acceleration.y, a.acceleration.z));

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

String accelerationCalc(double x, double y, double z) {
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
