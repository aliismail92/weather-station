import paho.mqtt.client as mqttClient
from datetime import datetime
from backports.datetime_fromisoformat import MonkeyPatch
import time
import database as db
MonkeyPatch.patch_fromisoformat()

temp, humidity, pressure, co2, o2, lux = [],[],[],[],[],[]
msg_received = False
lastrow_id = 1
 

#Functions Definitions
def on_connect(client, userdata, flags, rc):
    
    if rc == 0:
        print("Connected to broker with code", rc)
        client.connected_flag = True                #Signal connection 

    else:
        print("Connection failed with code", rc)

 
def on_message(client, userdata, message):
    print ("Message received: ", message.payload)
    global msg_received
    global data

    
    pay_load = str(message.payload, 'utf-8')
    data = pay_load.split()
    if (len(data) == 7):
        msg_received = True

def set_mqtt():

    broker_address= "192.168.1.11"  #Broker address
    port = 1883                     #Broker port
    user = "admin"                  #Connection username
    password = "admin"              #Connection password

    mqttClient.Client.connected_flag=False 
    client = mqttClient.Client("Python")#, protocol=mqttClient.MQTTv31)  #create new instance
    client.username_pw_set(username=user,password=password)    #set username and password
    client.on_connect= on_connect              #attach function to callback
    client.on_message= on_message              #attach function to callback
    client.connect(broker_address, port=port)          #connect to broker
    client.loop_start()        #start the loop
    count  = 0

    while not client.connected_flag:    #Wait for connection
        time.sleep(1)
        print ("waiting for connection", count)
        count +=1
        
    topics = [("SenseData",2), ("broker",2)]
    client.subscribe(topics)


#Code Setup
set_mqtt()
db.create_table()

if type(db.get_bound("DESC")) is type(None):
    start_date = datetime.today()
    
else:
    start_row = db.get_bound("ASC")
    end_row = db.get_bound("DESC")
    start_date_iso = start_row[1]
    start_date = datetime.fromisoformat(start_date_iso)

#Data acquisotion loop
try:
    while True:
        time.sleep(0.5)
        if msg_received == True:

            now = datetime.today()
            elapsed = now - start_date 
            seconds = elapsed.seconds
            days = elapsed.days
            date = now.isoformat()

            lastrow_id = db.insert(date, days, seconds, data[0],data[5], data[1], data[2],data[3], data[4], data[6])
            msg_received = False
            
        

except KeyboardInterrupt:
    print ("exiting")
    client.disconnect()
    client.loop_stop()