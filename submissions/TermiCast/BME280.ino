#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme;

void setup() {
  Serial.begin(9600);
  if (!bme.begin(0x76)) {
    Serial.println("ERROR: BME280 not found!");
    while (1);
  }
}

void loop() {
  float temperature = bme.readTemperature();
  float humidity = bme.readHumidity();
  float pressure = bme.readPressure() / 100.0F;

  Serial.print("TEMP:");
  Serial.print(temperature);
  Serial.print(",HUMIDITY:");
  Serial.print(humidity);
  Serial.print(",PRESSURE:");
  Serial.println(pressure);

  delay(2000);
}