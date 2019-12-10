import RPi.GPIO as GPIO
import time
import requests
import face_recognition
import picamera
import numpy as np
import time
from subprocess import call
from PIL import Image
import threading
import time
#import send_email
import paho.mqtt.client as mqtt
import os
from urllib import parse as urlparse
import pygame



def scan_run(start_time):
    global flag
    lock = 15
    unlock = 14
    output = np.empty((720, 1280, 3), dtype=np.uint8)

    # Load a sample picture and learn how to recognize it.
    print("Loading known face image(s)")
    obama_image = face_recognition.load_image_file("06.png")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    while True:
        if time.time() - start_time < 20:
            print("Capturing image.")
            # Grab a single frame of video from the RPi camera as a numpy array
            #camera.capture(output, format="rgb")
            call(["fswebcam","-d","/dev/video0","-r","1280x720","--no-banner","sample.jpg"],5)
            output  = Image.open("sample.jpg")
            output = np.array(output)
            print(output.shape)
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(output)
            print("Found {} faces in image.".format(len(face_locations)))
            face_encodings = face_recognition.face_encodings(output, face_locations)

            # Loop over each face found in the frame to see if it's someone we know.
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                match = face_recognition.compare_faces([obama_face_encoding], face_encoding)
                name = "<Unknown Person>"

                if match[0]:
                    name = "Owner"
                    print("I see someone named {}!".format(name))
                    GPIO.output(unlock,True)
                    GPIO.output(lock, False)   
                    break
                else:
                    r = requests.post('https://maker.ifttt.com/trigger/intruder_alert/with/key/2tdua3kemvxJYEY3ksUoi', params={"value1":str(time),"value2":"none","value3":"none"})
                    #send_email.send_an_email()
                    print("intruder")
        else:
            print("TIMEOUT REACHED")
            break
def motion_sense():
    TRIG = 20
    ECHO = 21
    unlock = 14
    lock = 15

    try:
        
        while True:

            GPIO.output(TRIG, False)
            print("Waiting For Sensor To Settle")
            time.sleep(2)

            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)

            while GPIO.input(ECHO)==0:
              pulse_start = time.time()

            while GPIO.input(ECHO)==1:
              pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start

            distance = pulse_duration * 17150

            distance = round(distance, 2)
            if distance < 50:
                start_time = time.time()
                scan_run(start_time)    
            print("Distance:",distance,"cm")

    except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
        print("Cleaning up!")
        GPIO.cleanup()

if __name__ == "__main__":
       
    GPIO.setmode(GPIO.BCM)

    TRIG = 20
    ECHO = 21
    unlock = 14
    lock = 15

    print("Distance Measurement In Progress")

    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.setup(unlock,GPIO.OUT)
    GPIO.setup(lock,GPIO.OUT)
    GPIO.output(unlock,True)
    GPIO.output(lock, False)

    flag = 0
    def on_connect(client, userdata, flags, rc):
        print("rc: " + str(rc))

    def on_message(client, obj, msg):
        unlock = 14
        lock = 15
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        if msg.topic == "Alarm" and msg.payload == b'ON':
            GPIO.output(lock,True)
            GPIO.output(unlock, False)
            pygame.mixer.init()
            pygame.mixer.music.load("analog-watch-alarm_daniel-simion.wav")       
            pygame.mixer.music.play()
            
        if msg.topic == "Alarm" and msg.payload == b'LOCK':
            GPIO.output(lock,True)
            GPIO.output(unlock, False)
            #pygame.mixer.deinit()
           
        if msg.topic == "Alarm" and msg.payload == b'UNLOCK':
            GPIO.output(unlock,True)
            GPIO.output(lock, False)
            pygame.mixer.init()
            pygame.mixer.music.load("hello-2.wav")       
            pygame.mixer.music.play()
        
           # while pygame.mixer.music.get_busy() == True:
             #   pygame.mixer.music.load("analog-watch-alarm_daniel-simion.mp3")
              #  continue
            

    def on_publish(client, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(client, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(client, obj, level, string):
        print(string+"1" )
    t1 = threading.Thread(target=motion_sense)
    t1.start()
    mqttc = mqtt.Client()
    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe

    # Uncomment to enable debug messages
    #mqttc.on_log = on_log

    # Parse CLOUDMQTT_URL (or fallback to localhost)
    url_str = os.environ.get('CLOUDMQTT_URL', 'tailor.cloudmqtt.com')
    url = urlparse.urlparse(url_str)
    #topic = url.path[1:] or 'test'
    #print(topic)
    topic = 'Alarm'

    # Connect
    #mqttc.username_pw_set(url.username, url.password)
    mqttc.username_pw_set('wgwiciob', '4WExHXCt7b09')
    #mqttc.connect(url.hostname, url.port)
    mqttc.connect('tailor.cloudmqtt.com', 14422)

    # Start subscribe, with QoS level 0
    mqttc.subscribe(topic, 0)

    # Publish a message
    #mqttc.publish(topic, "ON")


    # Continue the network loop, exit when an error occurs
    rc = 0
    while rc == 0:
        rc = mqttc.loop()
    print("rc: " + str(rc))
    

