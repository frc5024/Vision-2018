import numpy as np
import cv2
import logging
import imutils
import math
from networktables import NetworkTables
import grip
import urllib
import time

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--netcam", help="Use the camera over CScore server")
args = parser.parse_args()


CameraWidth = 640
CameraHeight = 480
FieldOfView = 60
DegPerPixel = FieldOfView/CameraWidth
FocalLength = (CameraWidth/2)/ (math.tan(FieldOfView/2*(math.pi/180)))
Displacement = 19 # this is the verticall distance between camera and cube, need to be measured.
if not args.netcam:
    feed = cv2.VideoCapture(0)
else:
	try:
		stream = urllib.request.urlopen("http://roborio-5024-frc.local:1184/stream.mjpg")
	except:
		print("Could not open stream!")
		exit(1)
	bytes = ''
speedLimit = 100
MinDistance = 30

#initialize table
NetworkTables.initialize(server='roborio-5024-frc.local')
Table = NetworkTables.getTable('SmartDashboard')


pipeline = grip.GripPipeline()

print("Camera Data:")
while True:
    if not args.netcam:
        _,frame= feed.read()
        key= cv2.waitKey(20)
    else:
        bytes += stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg   = bytes[a:b+2]
            bytes = bytes[b+2:]
            frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
        else:
        	print("Improper data fron netcam", end="\r")
        	continue
        # frame = np.array(bytearray(frame), dtype=np.uint8)
        # frame = cv2.imdecode(frame, -1)
    
    cv2.imshow("RAW",frame)
    
    pipeline.process(frame)
    
    contours = pipeline.convex_hulls_output
    #if there are multiple contours, the one with max area is the box
    if len(contours) < 1:
        continue
    
    box=max(contours, key=cv2.contourArea)
    (xg,yg,wg,hg) = cv2.boundingRect(box)
    CubeData = [xg, yg, wg, hg]
    CenterOfCube = xg + (wg/2)
    CenterOfCubeVert = yg + (hg/2)
    ImageSizeInDeg = CenterOfCube * DegPerPixel
    PixelsToCube = CenterOfCube - CameraWidth/2
    PixelsToCubeVert = CenterOfCubeVert - CameraHeight/2

    #AngleToCube = ((CenterOfCube - (CameraWidth/2)) * DegPerPixel)
    #more accurate angle:
    AngleToCube = (math.atan(PixelsToCube/FocalLength))*(180/math.pi)
    AngleToCubeVert = (math.atan(PixelsToCubeVert/FocalLength))
    DistanceToCube = Displacement / math.tan(AngleToCubeVert) if math.tan(AngleToCubeVert) != 0 else 0
    
    # Draw secondary display
    cv2.rectangle(frame,(xg,yg),(xg+wg,yg+hg),(0,255,0),2)
    cv2.imshow("Filtered", frame)
    
    # Saftey checks
    DistanceToCube = 0 if DistanceToCube <=0 else DistanceToCube
    # DistanceToCube = speedLimit if DistanceToCube > speedLimit else DistanceToCube
    DistanceToCube = 0 if DistanceToCube <= MinDistance else DistanceToCube

    #send data to table
    print(f"D: {DistanceToCube} | R: {AngleToCube}                     ", end="\r")
    Table.putNumber("DistanceToCube", DistanceToCube * -1)
    Table.putNumber("PixelsToCube", PixelsToCube)
    Table.putNumberArray("X, Y, W, H", CubeData)
    Table.putNumber("CenterOfCube", CenterOfCube)
    Table.putNumber("AngleToCube", AngleToCube)
