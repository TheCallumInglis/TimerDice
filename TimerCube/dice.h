#include <Adafruit_MPU6050.h>
#include <FastLED.h>

Adafruit_MPU6050 mpu;
CRGB leds[LED_COUNT]; // Neopixel

/** Compare given acceleration value with a threshold. 
 * Fuzziness allows for approximation of value <-> threshold comparison. 
 * 
 * @param value Acceleration Value to Compare
 * @param threshold Acceleration Value to Compare Against
 * @returns True when value approximately matches threshold
 * @note ACCELERATION_ZERO_THRESHOLD defines the "fuzziness" of our comparison. Adjust as needed.
*/
bool FuzzyCompare(double value, double threshold) {
  return 
    value >= (threshold - ACCELERATION_ZERO_THRESHOLD) && 
    value <= (threshold + ACCELERATION_ZERO_THRESHOLD);
}

/** Get the dice face as a number from acceleration data
 * Calculated relative to X Axis for a 12-sided dice
 * 
 * TODO Make generic for any number of faces
 * 
 * @param x Acceleration on X axis
 * @param y Acceleration on Y axis
 * @param z Acceleration on Z axis
 * @returns Face number as integer, 0 on error / non-deterministic face
*/
int GetDiceFace(double x, double y, double z) {
  if (FuzzyCompare(x, -9.8)) { // X roughly -9.8
    if (y < 0) { return 6; } else { return 11; }
  }

  if (FuzzyCompare(x, -4.5)) { // X roughly -4.5
    if (y < 0) { return 5; } else { return 7; }
  }
  
  if (FuzzyCompare(x, 0.0)) { // X roughly 0
    if (FuzzyCompare(y, -9.8)) {
      return 1;
    } else if (FuzzyCompare(y, -4.5)) {
      return 2;
    } else if (FuzzyCompare(y,  4.5)) {
      return 10;
    } else if (FuzzyCompare(y,  9.0)) {
      return 12;
    }
  }

  if (FuzzyCompare(x, 4.5)) { // X roughly 4.5
    if (y < 0) { return 4; } else { return 8; }
  }

  if (FuzzyCompare(x, 9.8)) { // X roughly 9.8 
    if (y < 0) { return 3; } else { return 9; }
  }

  return 0; // We broke it!
}

int GetDiceFaceNow() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  return GetDiceFace(a.acceleration.x, a.acceleration.y, a.acceleration.z);
}

void blink(uint8_t Pin, int Count, int Duration) {
  for (int i = 0; i < Count; i++) {
    digitalWrite(Pin, HIGH); 
    delay(Duration/2);
    digitalWrite(Pin, LOW);
    delay(Duration/2);
  }
}

/** Neopixel **/
void SetDiceColour(int face) {

  // https://github.com/FastLED/FastLED/wiki/Pixel-reference#predefined-colors-list
  CRGB faceColours[] = {
    CRGB::Black,      // 0 i.e. Off
    CRGB::Red,        // 1
    CRGB::Blue,       // 2
    CRGB::Green,      // 3
    CRGB::Orange,     // 4
    CRGB::BlueViolet, // 5
    CRGB::Chartreuse, // 6
    CRGB::Cyan,       // 7
    CRGB::Magenta,    // 8
    CRGB::Grey,       // 9
    CRGB::Maroon,     // 10
    CRGB::OrangeRed,  // 11
    CRGB::Aquamarine  // 12 
  };

  for (int i = 0; i < LED_COUNT; i++) {
    leds[i] = faceColours[face];
  }

  FastLED.show();
  FastLED.delay(10);
}

void ClearDiceColour() {
  SetDiceColour(0);
}

