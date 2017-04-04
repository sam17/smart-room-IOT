
#include <SPI.h>
#include <WiFi.h>
/*macro definitions of PIR motion sensor pin and LED pin*/
#define PIR_MOTION_SENSOR 2//Use pin 2 to receive the signal from the module
#define LED 8//the Grove - LED is connected to D4 of Arduino

char ssid[] = "loadsofpeace"; //  your network SSID (name) 
char pass[] = "soumyadeep";  

WiFiClient client;
char server[] = "192.168.43.120";
int port=3000;
int status = WL_IDLE_STATUS;
boolean prevState = false;//true for people in
boolean lastConnected = false;     

void setup()
{
  Serial.begin(115200);
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present"); 
    // don't continue:
    while(true);
   } 
   while (status != WL_CONNECTED) { 
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:    
    status = WiFi.begin(ssid, pass);
    // wait 10 seconds for connection:
    delay(10000);
  } 
  Serial.println("Connected to wifi");
  printWifiStatus();
    
  Serial.println("Starting .....");
  Serial.println("PIR Motion on 2...");
  pinMode(PIR_MOTION_SENSOR, INPUT);
  pinMode(LED,OUTPUT);
  delay(1000);
  prevState = isPeopleDetected();
}

void loop()
{
  if (!client.connected() && lastConnected) {
    Serial.println();
    Serial.println("disconnecting.");
    client.stop();
  }
  
   if(isPeopleDetected()) { //if it detects the moving people?
        digitalWrite(LED, HIGH);
        if(prevState == false){
           callRequest("1");
        }
       
        prevState = true;
    }
    else {
        digitalWrite(LED, LOW);
         if(prevState == true){
           callRequest("0");
        }
        prevState = false;
    }
     delay(2000);
}


/***************************************************************/
/*Function: Detect whether anyone moves in it's detecting range*/
/*Return:-boolean, true is someone detected.*/
boolean isPeopleDetected()
{
    int sensorValue = digitalRead(PIR_MOTION_SENSOR);
    Serial.print("SensorValue:");
    Serial.println(sensorValue);
    if(sensorValue == HIGH)//if the sensor value is HIGH?
    {
        return true;//yes,return true
    }
    else
    {
        return false;//no,return false
    }
   
}

void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void callRequest(String statuscode) {
   Serial.println("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  if(!client.connected())
  {
    client.connect(server, port);
  }
  if (client.connected()) {
    Serial.println("connected to server");
    // Make a HTTP request:
    client.println("GET /toggleOccupiedStatus?room=Saturn&status=" + statuscode + " HTTP/1.1");
    client.println("Host: " + String(server));
    client.println("Connection: close");
    client.println();
    while (client.available()) {
     char c = client.read();
     Serial.write(c);
    }
  } 
 // if (!client.connected()) {
  //  Serial.println();
  //  Serial.println("disconnecting from server.");
   // client.stop();
  //}
  delay(2000);
}

