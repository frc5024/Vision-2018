import numpy as np
import cv2
import logging
import imutils
import math
from networktables import NetworkTables
import grip


CameraWidth = 640
CameraHeight = 320
FieldOfView = 60
DegPerPixel = FieldOfView/CameraWidth
FocalLength = (CameraWidth/2)/ (math.tan(FieldOfView/2*(math.pi/180)))
Displacement = 30 # this is the verticall distance between camera and cube, need to be measured.


#initialize table
NetworkTables.initialize(server='10.50.24.2')
Table = NetworkTables.getTable('SmartDashboard')


#change this
inputImage= cv2.imread("cube.jpg",cv2.IMREAD_COLOR )
pipeline = grip.GripPipeline()


while True:
    pipeline.process(inputImage)
    contours = pipeline.convex_hulls_output
    #if there are multiple contours, the one with max area is the box
    box=max(contours, key=cv2.contourArea)
    (xg,yg,wg,hg) = cv2.boundingRect(box)
    CubeData = [xg, yg, wg, hg]
    CenterOfCube = xg + (wg/2)
    CenterOfCubeVert = yg + (hg/2)
    ImageSizeInDeg = CenterOfCube * DegPerPixel
    PixelsToCube = CenterOfCube - CameraWidth/2
    PixelsToCubeVert = CenterOfCubeVert - cameraHeight/2

    #AngleToCube = ((CenterOfCube - (CameraWidth/2)) * DegPerPixel)
    #more accurate angle:
    AngleToCube = (math.atan(PixelsToCube/FocalLength))*(180/math.pi)
    AngleToCubeVert = (math.atan(PixelsToCubeVert/FocalLength))
    DistanceToCube = Displacement / math.tan(AngleToCubeVert)

    #send data to table
    Table.putNumber("DistanceToCube", DistanceToCube)
    Table.putNumber("PixelsToCube", PixelsToCube)
    Table.putNumberArray("X, Y, W, H", CubeData)
    Table.putNumber("CenterOfCube", CenterOfCube)
    Table.putNumber("AngleToCube", AngleToCube)
