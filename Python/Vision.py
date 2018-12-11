import numpy as np
import cv2
import logging
import imutils
import math
from networktables import NetworkTables
import grip
import urllib
import time


CameraWidth = 640
CameraHeight = 480
FieldOfView = 60
DegPerPixel = FieldOfView/CameraWidth
FocalLength = (CameraWidth/2)/ (math.tan(FieldOfView/2*(math.pi/180)))
Displacement = 19 # this is the verticall distance between camera and cube, need to be measured.
feed = cv2.VideoCapture(0)

#initialize table
NetworkTables.initialize(server='10.50.24.2')
Table = NetworkTables.getTable('SmartDashboard')


pipeline = grip.GripPipeline()


while True:
    _,frame= feed.read()
    key= cv2.waitKey(20)
    # frame = np.array(bytearray(frame), dtype=np.uint8)
    # frame = cv2.imdecode(frame, -1)
    cv2.imshow("img",frame)
    pipeline.process(frame)
    
    contours = pipeline.convex_hulls_output
    #if there are multiple contours, the one with max area is the box
    if len(contours) < 1:
        continue
    print(1)
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

    #send data to table
    Table.putNumber("DistanceToCube", DistanceToCube * -1)
    Table.putNumber("PixelsToCube", PixelsToCube)
    Table.putNumberArray("X, Y, W, H", CubeData)
    Table.putNumber("CenterOfCube", CenterOfCube)
    Table.putNumber("AngleToCube", AngleToCube)
