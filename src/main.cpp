#include <Adafruit_ADS1015.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_BMP280.h>
//#include "CO2Sensor.h"
#include <dhtnew.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Arduino.h>

//Co2 Sensor
//CO2Sensor co2Sensor(A0, 0.99, 100);

//Aanalog I2C
Adafruit_ADS1115 ads(0x49);

//BMP Sensor
Adafruit_BMP280 bmp; // use I2C interface


//DHT Sensor
DHTNEW dht(D5); 


//Define WIFI
const char* ssid = "LeBgEnD";                   // wifi ssid
const char* password =  "ali12345";         // wifi password

//MQTT Settings
const char* mqttServer = "192.168.1.11";    // IP adress Raspberry Pi
const int mqttPort = 1883;
//const char* mqttUser = "mqtt1";      // if you don't have MQTT Username, no need input
//const char* mqttPassword = "mqtt1";  // if you don't have MQTT Password, no need input
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

//Variables
float dht22_temp,dewPoint, dht22_hum, bmp280_t, bmp280_p, co2_conc, o2_conc, lux;
unsigned long lastReconnectAttempt = 0;
unsigned long lastlooptime = 0;
float temperature;

//Functions
float readO2();
void bmpReading();
float light_sensor();
void dht_sensor();
void callback(char* topic, byte* payload, unsigned int length);
void send_mqtt_data();
bool reconnect();
double dewPointFast(double celsius, double humidity);

void setup() {
  
  Serial.begin(115200); 
  
  //Setting up Wifi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  //Setting up MQTT
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  //Setting up the sensors
  ads.begin(); 
  delay(50);
  bmp.begin();
  delay(50);


  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */

  //co2Sensor.calibrate();

}

void loop() {
  
  unsigned long now = millis();
  if ((now - lastlooptime) >= 600000){
      if (!client.connected()) {
          if (now - lastReconnectAttempt > 5000) {
          lastReconnectAttempt = now;
          // Attempt to reconnect
            if (reconnect()) {
              lastReconnectAttempt = 0;
            }
          }
  } else {
    
    //read sensors
    o2_conc = readO2();
    delay(100);
    co2_conc = 400;
    delay(100);
    bmpReading();
    delay(100);
    dht_sensor();
    delay(100);
    lux = light_sensor();

    //Average Temp
    temperature = (bmp280_t + dht22_temp)/2;
    //Dew Point Temp
    dewPoint = dewPointFast(dht22_temp, dht22_hum);
    //send sensor data
    send_mqtt_data();
    lastlooptime = now;

  }
  client.loop();
  }  
}

float readO2(){
    long sum = 0;
    for(int i=0; i<32; i++)
    {
        sum += ads.readADC_SingleEnded(0);
    }
        
    sum >>= 5;
     
    float MeasuredVout = sum * (3.3 / 17820.0);
    float Concentration = MeasuredVout * 0.21 / 1.42;
    float Concentration_Percentage=Concentration*100;
    return Concentration_Percentage;
}


void bmpReading(){

  bmp280_t = bmp.readTemperature()- 1;// -1 since BMP gives higher temp value
  bmp280_p = bmp.readPressure()/1000;
}

float light_sensor(){
  float volt = ads.readADC_SingleEnded(2);
  int intensity =map (volt, 0, 17820, 0, 100);
  return intensity;
}

void dht_sensor(){
    
    dht.read();
    dht22_hum = dht.getHumidity();
    dht22_temp= dht.getTemperature();
}
double dewPointFast(double celsius, double humidity)
{
        double a = 17.271;
        double b = 237.7;
        double temp = (a * celsius) / (b + celsius) + log(humidity/100);
        double Td = (b * temp) / (a - temp);
        return Td;
}

float getCO2(){
    float v = 0;
    for (int i = 0; i < 100; i++)
  {
    v += ads.readADC_SingleEnded(3);
     delay(20);
  }

  return v/100.0;
}
void callback(char* topic, byte* payload, unsigned int length) {

  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }

} 

void send_mqtt_data(){
  String payload = String(dht22_temp) + " " + String(dht22_hum) + " " + String(bmp280_p) + " " + String(co2_conc) + " " + String(o2_conc) + " " + String(dewPoint) + " " + String(lux) + " ";
  payload.toCharArray(msg, payload.length());
  Serial.println(payload);
  //client.publish("SenseData", msg);
  String playload2 = String(bmp280_t);
  playload2.toCharArray(msg, playload2.length());
  //client.publish("TempBmp", msg);
  String playload3 = String(dht22_temp);
  playload3.toCharArray(msg, playload3.length());
  //client.publish("TempDH22", msg);
  
}

bool reconnect() {
  
   // Create a random client ID
    String clientId = "ESP8266Client-";
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      // ... and resubscribe
      client.subscribe("inTopic");
      return true;
    } 
    else{
      return false;
    }
  
}