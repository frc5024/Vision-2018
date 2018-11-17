import numpy as np
import cv2
import logging
import imutils
import math
from networktables import NetworkTables
import grip


CameraWidth = 640
FieldOfView = 60
DegPerPixel = FieldOfView/CameraWidth

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
    #what is deg per pixel in our own setup?
    ImageSizeInDeg = CenterOfCube * DegPerPixel

    DistanceToCube = ((13/math.tan(math.radians(ImageSizeInDeg))))

    PixelsToCube = CenterOfCube - 300
    #also this
    AngleToCube = ((CenterOfCube - (CameraWidth/2)) * DegPerPixel)

    #send data to table
    Table.putNumber("DistanceToCube", DistanceToCube)
    Table.putNumber("PixelsToCube", PixelsToCube)
    Table.putNumberArray("X, Y, W, H", CubeData)
    Table.putNumber("CenterOfCube", CenterOfCube)
    Table.putNumber("AngleToCube", AngleToCube)
    Table.putBoolean("ContoursFound", True)
    
