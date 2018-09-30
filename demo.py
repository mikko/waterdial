import numpy as np
import cv2
import dial
import math

_DIAL_SCALE_ANGLE = 360 / 10
_ANGLE_OFFSET = -15 # scam

cap = cv2.VideoCapture('test.webm')

cv2.namedWindow('original')
cv2.namedWindow('frame')
cv2.moveWindow('original', 0,30) 
cv2.moveWindow('frame', 640,30) 

prevValue = -1
total = 0

while(cap.isOpened()):
    
    #######################
    # 1. Original frame

    ret, origFrame = cap.read()
    # Flip the frame because the camera is upside down
    origFrame = cv2.flip(origFrame, -1)
    frame = origFrame.copy()
    

    #######################
    # 2. Red mask
    frame = dial._mask(frame)
    
    #######################
    # 3. Threshold
    frame = dial._threshold(frame)
    
    #######################
    # 4. Contour calculation
    contours_image = origFrame.copy()
    contours = dial._contours(frame)
    cv2.drawContours(contours_image, contours, -1, (0, 255, 0), 1)
    frame = contours_image

    for c in contours:
        #######################
        # 5. Calculate extreme points for every contour
        extremes = dial._get_extremes(c)
        cv2.circle(frame, extremes[0], 5, (0, 0, 255), -1)
        cv2.circle(frame, extremes[1], 5, (0, 255, 0), -1)
        cv2.circle(frame, extremes[2], 5, (255, 0, 0), -1)
        cv2.circle(frame, extremes[3], 5, (255, 255, 0), -1)

        #######################
        # 6. Calculate "Center of mass" of each contour
        M = cv2.moments(c)
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        moment_point = tuple((center_x, center_y))
        cv2.circle(frame, moment_point, 5, (0, 0, 0), -1)
    
        #######################
        # 7. Calculate furthest point of extremes from the center
        distances = list(map(lambda x: dial._distance(moment_point, x), extremes))
        direction_point = extremes[distances.index(max(distances))]
        cv2.line(frame, moment_point, direction_point, (255, 255, 255), 3)

        #######################
        # 8. Calculate angle and value
        raw_angle = math.degrees(math.atan2(moment_point[0] - direction_point[0], moment_point[1] - direction_point[1]))
        angle = raw_angle if raw_angle > 0 else 360 + raw_angle
        angle = 360 - angle + _ANGLE_OFFSET
        
        dial_value = angle / _DIAL_SCALE_ANGLE
        roundedValue = int(dial_value)
        cv2.putText(frame, str(roundedValue), (moment_point[0], moment_point[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
    

    #######################
    # 9. Finally make the bookkeeping for the total
    litres = dial.get_litres(origFrame) % 100 # Fourth dial filtered out for demo purposes
    if (prevValue != -1):
        total = total + (litres - prevValue)
        cv2.putText(frame, "%.1f l" % total, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),2,cv2.LINE_AA)    
    prevValue = litres

    cv2.imshow('frame',frame)
    cv2.imshow('original',origFrame)
    
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

