#include <SD.h>

/** Write content to a file
 * @param filepath File to write to
 * @param content Content to be written
 * @returns True on succes, false otherwise
*/
bool WriteToFile(char* filepath, String content) {
    File data_file = SD.open(filepath, FILE_WRITE);
    
    if (!data_file) { 
        Serial.print("[WriteToFile] Error opening ");
        Serial.println(filepath);
        return false;
    }

    data_file.println(content);
    data_file.close();
    return true;
}

/** Does a given filepath exist
 * @param filepath File to check
 * @returns True if file exists
*/
bool FileExists(char* filepath) {
    return SD.exists(filepath);
}

/** Read Content of a file
 * @param filepath File to read
 * @returns Contents of file
*/
String ReadXMLFileContents(char* filepath) {
    File data_file = SD.open(filepath, FILE_READ);
    if (!data_file) { return ""; }

    // Read until nothing left
    String content;
    content += "<root>\n";
    while (data_file.available()) { 
        content += data_file.readStringUntil('\r');
    }
    content += "</root>";
    data_file.close();

    return content;
}
