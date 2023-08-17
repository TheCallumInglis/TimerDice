#include <RTClib.h>
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <TimeLib.h> 

RTC_DS1307 rtc;
WiFiUDP ntpUDP;
NTPClient time_client(ntpUDP, NTPServer);

// TODO Setup to work without hardware clock

/**
 * Get Current Date/Time and return in YYYY-MM-DDThh:mm:ss format
 * @returns date/timestamp
*/
String GetDateTimeNow() {
    char format[] = "YYYY-MM-DDThh:mm:ss";
    return rtc.now().toString(format);
}

/**
 * Set the Real Time Clock from NTP Server
*/
void UpdateRTCTime() {
    Serial.println("[RTC] :: Setting the time now...");

    if (time_client.update()) {
        rtc.adjust(DateTime(time_client.getEpochTime()));  // Set RTC time using NTP epoch time
        Serial.print("[RTC] :: The Time is Now: "); Serial.println(GetDateTimeNow());
        return;
    }

    Serial.println("[RTC] :: Failed to set the time");
}

/**
 * Setup the Real Time Clock, Set the Time from an NTP server
 * @returns True on success, false otherwise
*/
bool SetupRTC() {
    Serial.print("[RTC] :: Init...");

    if (!rtc.begin()) {
        Serial.println("Failed");
        return false;
    }
    Serial.println("Found!");

    // Set the time with NTP server
    time_client.begin();
    UpdateRTCTime();

    return true;
}
