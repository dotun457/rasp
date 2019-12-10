# This is a demo of running face recognition on a Raspberry Pi.
# This program will print out the names of anyone it recognizes to the console.

# To run this, you need a Raspberry Pi 2 (or greater) with face_recognition and
# the picamera[array] module installed.
# You can follow this installation instructions to get your RPi set up:
# https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65

import face_recognition
import picamera
import numpy as np
import time
from subprocess import call
from PIL import Image

# Get a reference to the Raspberry Pi camera.
# If this fails, make sure you have a camera connected to the RPi and that you
# enabled your camera in raspi-config and rebooted first.
#camera = picamera.PiCamera()
#camera.resolution = (320, 240)
flag = 0
start_time = time.time()
def scan_run(start_time):
    global flag
    output = np.empty((720, 1280, 3), dtype=np.uint8)

    # Load a sample picture and learn how to recognize it.
    print("Loading known face image(s)")
    obama_image = face_recognition.load_image_file("TINU.png")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    while True:
        if time.time() - start_time < 10:
            print("Capturing image.")
            # Grab a single frame of video from the RPi camera as a numpy array
            #camera.capture(output, format="rgb")
            call(["fswebcam","-d","/dev/video0","-r","1280x720","--no-banner","Tinu.jpg"],5)
            output  = Image.open("Tinu.jpg")
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
                    name = "Barack Obama"
                    print("I see someone named {}!".format(name))
                    flag = 2
                    break
                else:
                    print("intruder")
                    flag = 1
        else:
            break

#scan_run(start_time)        