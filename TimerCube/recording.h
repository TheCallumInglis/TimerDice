bool is_recording;
bool is_motion;
int recording_id;
char recording_file[32];
int face_recording;

void SetupRecording() {
    is_recording = false;
    is_motion = false;
    recording_id = 0;
    face_recording = 0;
}

/** Generate a unique recording file path
 * Within RECORDING_DIR:
 *    -> EPOCH-RAND.xml
 * 
 * @param out_recording_file Recording File Path
 */
void GetNewRecordingFilepath(char* out_recording_file) {
  char epoch_buffer[32]; // For epoch
  char id_buffer[6]; // For Recording ID
  char filepath[64]; // New filepath

  int epoch = (int)rtc.now().unixtime();
  sprintf(epoch_buffer, "%d", epoch);

  // Find unique filepath
  strcpy(filepath, "");
  while (strlen(filepath) == 0 || FileExists(filepath)) {
    recording_id = GetRandomTaskID();

    sprintf(id_buffer, "%d", recording_id);

    strcpy(filepath, RECORDING_DIR);
    strcat(filepath, epoch_buffer);
    strcat(filepath, "-");
    strcat(filepath, id_buffer);
    strcat(filepath, ".xml");
  }

  strcpy(out_recording_file, filepath);
}

/** Write recording data to XML File
 * @returns True on success, false on error
 */
bool StartRecordingFile(int face) {
    GetNewRecordingFilepath(recording_file);
    Serial.print("Recording File Path: "); Serial.println(recording_file);

    String data_string = "";
    data_string += "<deviceUID>"; data_string += GetDeviceUID(); data_string += "</deviceUID>\r\n"; // Device UID
    data_string += "<recordingID>"; data_string += recording_id; data_string += "</recordingID>\r\n"; // Recording ID (Local)
    data_string += "<face>"; data_string += face; data_string += "</face>\r\n"; // Dice Face
    data_string += "<start>"; data_string += GetDateTimeNow(); data_string += "</start>"; // Start Date/Time

    Serial.println(data_string);
    return WriteToFile(recording_file, data_string);
}

/** Start A Recording
 * Determine dice orientation, log recording start time to file, illuminate dice
 * @returns False on error, True otherwise
*/
bool StartRecording() {
    int search_direction_timeout = SEARCH_DIRECTION_THRESHOLD * 1000 / SEARCH_DIRECTION_INTERVAL;

    Serial.println("Starting Recording");
    blink(BUZZER, 1, 250);

    delay(450); // Allow time to position dice

    // Poll for direction until found or timeout reached
    Serial.print("[MOTION] Detecting Direction...");
    int face = 0;
    while (face == 0 && search_direction_timeout > 0) {
        delay(SEARCH_DIRECTION_INTERVAL);
        search_direction_timeout--;
        Serial.print(".");
        face = GetDiceFaceNow();
    }

    // Failed to determine direction
    if (face == 0) {
        Serial.println("Failed to detect direction after motion");
        blink(BUZZER, 1, 2000);

        is_recording = false;
        is_motion = false;
        return false;
    }
    Serial.println(face);

    // Log To File
    if(!StartRecordingFile(face)) {
        Serial.println("Failed to write recording to file");
        return false;
    }

    // TODO Sent to Server to notify start of recording

    SetDiceColour(face);
    face_recording = face;
    is_recording = true;

    return true;
}

/** Stop A Recording
 * Close out recording file, publish over MQTT to server
 * @returns False on error, True otherwise
*/
bool StopRecording() {
    Serial.println("Stopping Recording");
    blink(BUZZER, 2, 150);
        
    // Find the recording file we want to close
    if (!FileExists(recording_file)) {
        Serial.print("[StopRecording] Error opening (File does not exist): "); Serial.println(recording_file);
        return false;
        // TODO Maybe close off any "is recording" flags here...
    }

    // Close out recording file with an end time
    String data_string = "<end>"; data_string += GetDateTimeNow(); data_string += "</end>"; // End Date/Time
    Serial.println(data_string);

    if (!WriteToFile(recording_file, data_string)) {
        Serial.println("Failed to append recording file");
        return false;
        // TODO Maybe close off any "is recording" flags here...
    }

    ClearDiceColour(); // Turn off LEDs

    // Publish to MQTT Recording Finished
    String content = ReadXMLFileContents(recording_file);
    if (content.length() > 0) {
        String topic = "timer_mqtt/"; topic += recording_file; // Append recording file path to the topic
        Serial.println(content);

        if (!mqttClient.connected()) {
            Serial.println("MQTT Client is not connected! Reconnecting ..."); 
            ReconnectMQTT(); // TODO Timeout
            mqttClient.loop(); // Maintain MQTT Connection
        }
        
        if (mqttClient.publish(topic.c_str(), content.c_str())) {
            Serial.println("Msg Sent!");
            // TODO Archive recording file

        } else {
            Serial.println("Failed to send msg");
            // TODO Handle a failed to send msg
        }
    }

    is_recording = false;
    face_recording = 0;

    return true;
}

// void startRecordingTask(char* faceName) {
//   http.begin(client, API + "recording/start");
//   http.addHeader("Content-Type", "application/x-www-form-urlencoded");
//   http.addHeader("APIKEY", APIKEY);

//   String postData = "DiceUUID=" + getDeviceUID() + "&FaceName=" + faceName;

//   int httpCode = http.POST(postData);
//   String payload = http.getString();

//   Serial.println(postData);
//   Serial.println(httpCode);
//   Serial.println(payload);

//   http.end();
// }
