from dial import get_litres

import cv2

cap = cv2.VideoCapture(0)

# Scrap first frames to /dev/null for crappy cheap webcams doing
# something
for x in range(50):
    ret, frame = cap.read()
    if ret == False: # TODO: proper exit
        print("No frame available")
        break

if ret == True:
	meter_value = get_litres(frame)
	print("Send value to backend")
	print(meter_value)


cap.release()
cv2.destroyAllWindows()
