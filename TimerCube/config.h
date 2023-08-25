// Serial
#define SERIAL_BAUD 9600

// I/O
#define BUZZER D0
#define RECORDING_INDICATOR D4

#define LED_PIN   D3
#define LED_COUNT 10
#define LED_BRIGHTNESS 35
#define LED_TYPE  WS2811
#define LED_COLOUR_ORDER GRB

// Timing
#define LOOP_DELAY 100 // ms
#define SLACK 20
#define MOTION_DETECTION_THRESHOLD 35
#define MOTION_DETECTION_DURATION 100
#define SEARCH_DIRECTION_THRESHOLD 10 // Seconds to spend finding cube direction
#define SEARCH_DIRECTION_INTERVAL 250 // ms
#define ACCELERATION_ZERO_THRESHOLD 2 // G/s
#define FACE_SWITCH_THRESHOLD 4 // Seconds

// Dice
#define DICE_FACES 12

// SD Card
#define RECORDING_DIR "/recordings/"

// GY-521 Gryoscope
#define GRYO_I2C 0x69 // ADD Low, Addr = 0x68; ADD High, Addr = 0x69;

// RTC
#define NTPServer "uk.pool.ntp.org"