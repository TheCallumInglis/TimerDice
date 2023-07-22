// Network Config
#define WIFI_SSID "Up Up And Away"
#define WIFI_PASS "784Gtd6RBNxf"

// Device
String API = "http://10.0.100.22:7216/api/";
#define APIKEY "9EFC0B37-1CB2-47D9-BA2E-76F614DCE91B"

// Serial
#define SERIAL_BAUD 9600

// I/O
#define BUZZER D0

// Timing
#define SLACK 20
#define MOTION_DETECTION_THRESHOLD 35
#define MOTION_DETECTION_DURATION 100
#define SEARCH_DIRECTION_THRESHOLD 5 // Seconds
#define SEARCH_DIRECTION_INTERVAL 250 // ms
#define ACCELERATION_ZERO_THRESHOLD 3 // G/s

// Dice
#define DICE_FACES 6

// SD Card
#define RECORDING_FILE "recording.csv"

// GY-521 Gryoscope
#define GRYO_I2C 0x69 // ADD Low, Addr = 0x68; ADD High, Addr = 0x69;