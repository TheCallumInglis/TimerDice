#include <math.h>

#define RAND_TASK_ID_MIN 10000
#define RAND_TASK_ID_MAX 100000

/**
 * @return Random Task ID between RAND_TASK_ID_MIN and RAND_TASK_ID_MAX
*/
int GetRandomTaskID() {
    return rand() % RAND_TASK_ID_MAX + RAND_TASK_ID_MIN;
}

/** Create a device UID based on the harware MAC Address
 * @returns TIMERCUBE-XXXXXX where XXXXXX is a partial MAC address of the chip
*/
String GetDeviceUID() {
  return "TIMECUBE-" + String(ESP.getChipId());
}