import math
from math import pi

import numpy as np
import cv2

import threading

from urllib import request

import scipy.optimize as optimize
from peakutils.peak import indexes

import matplotlib.pyplot as plt

# import RPi.GPIO as GPIO

import time

urlA = "http://192.168.43.101:8080/?action=snapshot"
urlB = "http://192.168.43.100:8080/?action=snapshot"

color_dist = {
    'red1': {'lower': np.array([0, 43, 66]), 'upper': np.array([10, 255, 255])},
    'red2': {'lower': np.array([156, 43, 66]), 'upper': np.array([180, 255, 255])},
    'blue': {'lower': np.array([100, 80, 46]), 'upper': np.array([124, 255, 255])},
    'green': {'lower': np.array([35, 43, 35]), 'upper': np.array([90, 255, 255])},
    'pink': {'lower': np.array([130, 0, 35]), 'upper': np.array([180, 100, 255])},
    }

lower1=color_dist['red1']['lower']
upper1=color_dist['red1']['upper']
lower2=color_dist['red2']['lower']
upper2=color_dist['red2']['upper']

dataImage=np.zeros((640,360,3),dtype=np.uint8)
emptyImage = np.zeros((640,480,3),dtype=np.uint8)

thread_lock = threading.Lock()
thread_exit = False
Flag = 0
T1=time.time()
pointA=np.zeros((1,3))
pointB=np.zeros((1,3))

# # Pin Definitons:
# led_pin = 12  # BOARD pin 12
# bep_pin = 13  # BOARD pin 18
# but_pin = 7

def startMeasure(channel):
    global Flag
    print("Start Measuring")
    Flag = 2

    # GPIO.output(bep_pin, GPIO.HIGH)
    # time.sleep(0.1)
    # GPIO.output(bep_pin, GPIO.LOW)

# # Jetson GPIO initial
# def GPIO_init():
#     # Pin Setup:
#     GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
#     GPIO.setup(led_pin, GPIO.OUT)
#     GPIO.setup(bep_pin, GPIO.OUT)  
#     GPIO.setup(but_pin, GPIO.IN)

#     # Initial state for LEDs:
#     GPIO.output(led_pin, GPIO.LOW)
#     GPIO.output(bep_pin, GPIO.LOW)
#     GPIO.add_event_detect(but_pin, GPIO.FALLING, callback=startMeasure, bouncetime=200)

# # Get snapshot from url
# def downloadImg(url):
#     with request.urlopen(url) as f:
#         data = f.read()
#         img1 = np.frombuffer(data, np.uint8)
#         #print("img1 shape ", img1.shape) # (83653,)
#         img_cv = cv2.imdecode(img1, cv2.IMREAD_ANYCOLOR)
#         img_rot = np.rot90(img_cv)
#         return img_rot

# # Get frame from camera
def downloadImg(url):
    ret, img_cv= url.read()
    if ret:
        img_rot = np.rot90(img_cv)
        return img_rot
    else:
        return emptyImage

# Empty function
def empty(a):
    pass

# Target function
# x = a0 * sin(a1 * x + a2) + a3
def target_func(x, a0, a1, a2, a3):
    return a0 * np.sin(a1 * x + a2) + a3

# Measure the period and the length of single pendulum
def measure(point):
    # L = (10*T*T)/(2*pi)^2
    k = 10 / (4*pi*pi)
    # Get all the indexs of peak
    peak = indexes(point[1:, 0], min_dist=4)

    # print(point[peak, :])
    # print(peak)
    
    # valley = signal.argrelextrema(point[1:,0], np.less) 
    # print(point[valley, :])
    # print(valley)

    # Calculate the period and the length
    # The time difference between two adjacent peaks is the period
    period_ava = (point[peak[np.size(peak)-1], 2]-point[peak[0], 2]) / (np.size(peak)-1)
    # L = k*T*T
    length = k*period_ava*period_ava

    print( "T= "+str(period_ava)+"; L= "+str(length))

    return period_ava

# Locate the target
# Record the positions and the time of the target after starting to measure
def colorLocate(color_image, point):
    global T1
    global Flag
    global dataImage
    global lower1,upper1,lower2,upper2

    para = None

    imgResult = color_image.copy()
    # Gaussian Blur
    image_gus = cv2.GaussianBlur(color_image, (5, 5), 0)

    # Transfer rgb to hsv
    image_hsv=cv2.cvtColor(image_gus, cv2.COLOR_BGR2HSV)

    # # Erode image
    # erode_hsv = cv2.erode(image_hsv, None, iterations=3)
    # # Dilate image
    # kernel = np.ones((3,3),np.uint8) 
    # dilate_hsv = cv2.dilate(erode_hsv,kernel,iterations = 3)

    # kernel = np.ones((3,3),np.uint8)
    # # Open operation( erode and then dilate)
    # opening_hsv = cv2.morphologyEx(image_hsv, cv2.MORPH_OPEN, kernel)

    # Generate mask
    # mask = cv2.inRange(image_hsv,lower,upper)

    # mask1 = cv2.inRange(image_hsv,color_dist['red1']['lower'],color_dist['red1']['upper'])
    # mask2 = cv2.inRange(image_hsv,color_dist['red2']['lower'],color_dist['red2']['upper'])
    # mask = mask1+mask2
    mask1 = cv2.inRange(image_hsv,lower1,upper1)
    mask2 = cv2.inRange(image_hsv,lower2,upper2)
    mask = mask1+mask2
        
    # mask = cv2.inRange(image_hsv,color_dist['pink']['lower'],color_dist['pink']['upper'])
        
    # Set kernel as 3*3
    kernel = np.ones((3,3),np.uint8)
    # Erode image
    erode_mask = cv2.erode(mask, kernel, iterations=4)
    # Dilate image
    opening_mask = cv2.dilate(erode_mask, kernel, iterations=3)

    # # Open operation( erode and then dilate)
    # kernel = np.ones((5,5),np.uint8)
    # opening_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

    contours, hierarchy = cv2.findContours(erode_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if np.size(contours)>0:
        c = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        #rect = cv2.boundingRect(c)
        box = cv2.boxPoints(rect)
        cv2.drawContours(imgResult, [np.int0(box)], -1, (0, 0, 255), 2)
        cv2.circle(imgResult, tuple(map(int,list(rect[0]))), 2, (255, 0, 0), 2)

        if Flag != 0:
            if point.shape[0] == 1:
                T1=time.time()
                dataImage=np.zeros((640,360,3),dtype=np.uint8)

            T2 = time.time()
                
            point1=np.append(rect[0],T2-T1)
            #print(point1)
            point=np.append(point,np.array(point1).reshape(1,3), axis=0)
            # print(pointPos)

            # If record time is longer than 10 sec, stop recording and start to calculate
            if T2-T1>=10:
                Flag = Flag-1

                # Confirm that two cameras finish the measurement
                if Flag == 0:

                    # GPIO.output(led_pin, GPIO.HIGH)
                    # GPIO.output(bep_pin, GPIO.HIGH)
                    time.sleep(1)
                    # GPIO.output(led_pin, GPIO.LOW)
                    # GPIO.output(bep_pin, GPIO.LOW)

                # peak = signal.argrelextrema(point[:,0],np.greater)
                
                # Through the record points to get an approximate period
                period=measure(point)

                # Initial parament a0, a1, a2, a3
                a0=max(point[1:,0])-min(point[1:,0])
                a1=2*pi/period
                a2=0
                a3=240

                p0=[a0,a1,a2,a3]

                # Fit sin function and get the parameters
                para, _ = optimize.curve_fit(target_func, point[1:,2],point[1:,0],p0=p0)
                
                # L_fit = 9.78/para[1]/para[1]-0.072
                # print("L_fit= ", L_fit)

                # y_fit = [target_func(a, *para) for a in point[1:,2]]
                # plt.plot(point[1:,2], y_fit, 'g')
                # plt.scatter(point[1:,2],point[1:,0])
                # plt.show()
                
                # Empty the record
                point=np.zeros((1,3))
            
    return imgResult, erode_mask, point, para

class myThread(threading.Thread):
    def __init__(self, url, point):
        super(myThread, self).__init__()
        self.url = url
        self.point = point
        self.para = None
        self.frame = np.zeros((640,480,3),dtype=np.uint8)
        self.imgResult = np.zeros((640,480,3),dtype=np.uint8)
        self.erode_musk = np.zeros((640,480,3),dtype=np.uint8)

    def get_frame(self):
            return self.frame

    def get_imgResult(self):
            return self.imgResult

    def get_erode_musk(self):
            return self.erode_musk

    def get_para(self):
        return self.para

    def empty_para(self):
        self.para = None
    
    def run(self):
        global thread_exit

        while not thread_exit:
            fpsT1 = time.time()
            frame = downloadImg(self.url) 
            imgResult,erode_musk, point, para = colorLocate(frame, self.point)
            fpsT2 = time.time()
            fps =1/( fpsT2 - fpsT1)

            cv2.putText(imgResult,
                "{:.0f} FPS".format(fps),
                (int(480*0.7), int(640*0.1)),
                cv2.FONT_HERSHEY_SIMPLEX,1,
                (0,255,0),2,cv2.LINE_AA)

            thread_lock.acquire()
            self.frame = frame
            self.imgResult = imgResult
            self.erode_musk = erode_musk
            self.point = point
            if not para is None:
                self.para = para
            thread_lock.release()


def main():
    global thread_exit
    global Flag
    global lower1,upper1,lower2,upper2
    # GPIO_init()
    capA = cv2.VideoCapture(3)
    capB = cv2.VideoCapture(2)
    # threadA = myThread(urlA, pointA)
    # threadB = myThread(urlB, pointB)
    threadA = myThread(capA, pointA)
    threadB = myThread(capB, pointB)
    threadA.start()
    threadB.start()
    cv2.namedWindow('Trackbars')
    cv2.resizeWindow("Trackbars",640,400)

    # Trackbar seetings
    cv2.createTrackbar("H1min","Trackbars",  0,180,empty)
    cv2.createTrackbar("H1max","Trackbars",10,180,empty)
    cv2.createTrackbar("S1min","Trackbars",  43,255,empty)
    cv2.createTrackbar("S1max","Trackbars",255,255,empty)
    cv2.createTrackbar("Vmin","Trackbars",  0,255,empty)
    cv2.createTrackbar("Vmax","Trackbars",255,255,empty)
    cv2.createTrackbar("H2min","Trackbars",  156,180,empty)
    cv2.createTrackbar("H2max","Trackbars",180,180,empty)
    cv2.createTrackbar("S2min","Trackbars",  43,255,empty)
    cv2.createTrackbar("S2max","Trackbars",255,255,empty)

    while not thread_exit:
        h1_min = cv2.getTrackbarPos("H1min","Trackbars")
        h1_max = cv2.getTrackbarPos("H1max","Trackbars")
        s1_min = cv2.getTrackbarPos("S1min","Trackbars")
        s1_max = cv2.getTrackbarPos("S1max","Trackbars")
        v_min = cv2.getTrackbarPos("Vmin","Trackbars")
        v_max = cv2.getTrackbarPos("Vmax","Trackbars")
        h2_min = cv2.getTrackbarPos("H2min","Trackbars")
        h2_max = cv2.getTrackbarPos("H2max","Trackbars")
        s2_min = cv2.getTrackbarPos("S2min","Trackbars")
        s2_max = cv2.getTrackbarPos("S2max","Trackbars")
        # Get lower and upper array
        lower1 = np.array([h1_min,s1_min,v_min])
        upper1 = np.array([h1_max,s1_max,v_max])
        lower2 = np.array([h2_min,s2_min,v_min])
        upper2 = np.array([h2_max,s2_max,v_max])

        thread_lock.acquire()
        frameA = threadA.get_frame()
        imgResultA = threadA.get_imgResult()
        paraA = threadA.get_para()
        frameB = threadB.get_frame()
        imgResultB = threadB.get_imgResult()
        paraB = threadB.get_para()
        erodeA=threadA.get_erode_musk()
        erodeB=threadB.get_erode_musk()
        thread_lock.release()
        
        if (not paraA is None) and (not paraB is None):
            TA = 2*pi/paraA[1]
            LA_fit = (9.802/paraA[1]/paraA[1]-0.0738)*100
            TB = 2*pi/paraB[1]
            LB_fit = (9.802/paraB[1]/paraB[1]-0.0738)*100
            theta = math.atan2(abs(paraA[0]),abs(paraB[0]))/pi*180
            
            if abs(LA_fit-LB_fit)>=4:
                if abs(paraA[0])-abs(paraB[0]) >0:
                    L_ave=LA_fit
                else:
                    L_ave=LB_fit
            else :
                L_ave = (LA_fit+LB_fit)/2

            print("LengthA: "+str(LA_fit)+"; PeriodA: "+str(TA))
            print("LengthB: "+str(LB_fit)+"; PeriodB: "+str(TB))
            print(theta)

            print(paraA[0],paraB[0])
            print(theta)

            cv2.putText(dataImage,
                "Length: {:>5.2f} cm".format(L_ave),
                (int(240*0.05), int(640*0.1*1)),
                cv2.FONT_HERSHEY_SIMPLEX,1,
                (0,255,0),2,cv2.LINE_AA)

            cv2.putText(dataImage,
                "Theta: {:>2.2f} degree".format(theta),
                (int(240*0.05), int(640*0.1*2)),
                cv2.FONT_HERSHEY_SIMPLEX,1,
                (0,255,0),2,cv2.LINE_AA)

            cv2.putText(dataImage,
                "LengthA: {:>5.2f} cm".format(LA_fit),
                (int(240*0.05), int(640*0.1*4)),
                cv2.FONT_HERSHEY_SIMPLEX,1,
                (0,255,0),2,cv2.LINE_AA)

            cv2.putText(dataImage,
                "PeriodA: {:>5.3f} s".format(TA),
                (int(240*0.05), int(640*0.1*5)),
                cv2.FONT_HERSHEY_SIMPLEX,1,
                (0,255,0),2,cv2.LINE_AA)
            
            cv2.putText(dataImage,
                "LengthB: {:>5.2f} cm".format(LB_fit),
                (int(240*0.05), int(640*0.1*6)),
                cv2.FONT_HERSHEY_SIMPLEX,1,
                (0,255,0),2,cv2.LINE_AA)

            cv2.putText(dataImage,
                "PeriodB: {:>5.3f} s".format(TB),
                (int(240*0.05), int(640*0.1*7)),
                cv2.FONT_HERSHEY_SIMPLEX,1,
                (0,255,0),2,cv2.LINE_AA)



            thread_lock.acquire()
            threadA.empty_para()
            threadB.empty_para()
            thread_lock.release()

        # imgStack = stackImages(0.5,([imgResultA, imgResultB]))
        # imgStack = stackImages(0.5,([color_imageA, color_imageB]))
        cv2.namedWindow('Trace', cv2.WINDOW_AUTOSIZE)
        imgStack = np.hstack((imgResultA, imgResultB, dataImage))
        cv2.imshow('Trace',imgStack)

        #cv2.namedWindow('Erode', cv2.WINDOW_AUTOSIZE)
        #imgStack = np.hstack((erodeA,erodeB))
        #cv2.imshow('Erode',imgStack)
        
        key = cv2.waitKey(1)

         # Press 'm' to measure the period
        if key & 0xFF == ord('m'):
            Flag = 2
            print("Start to measure.")
            # GPIO.output(bep_pin, GPIO.HIGH)
            # time.sleep(0.1)
            # GPIO.output(bep_pin, GPIO.LOW)
            

        if key & 0xFF == ord('q'):
            thread_exit = True

    # GPIO.cleanup()
    threadA.join()
    threadB.join()

if __name__ == "__main__":
    main()