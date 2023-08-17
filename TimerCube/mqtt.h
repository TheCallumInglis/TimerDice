#include <ESP8266HTTPClient.h>
#include <PubSubClient.h> // MQTT Library: https://pubsubclient.knolleary.net/api
                          // With help from https://funprojects.blog/2018/12/07/rabbitmq-for-iot/

WiFiClient client;                       
PubSubClient mqttClient(client); // Rabbit MQ

void ReconnectMQTT() {
  // Loop until we're reconnected
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");

    // Attempt to connect
    if (mqttClient.connect(GetDeviceUID().c_str(), MQTT_USER, MQTT_PASS)) {
      Serial.println("connected");

    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}