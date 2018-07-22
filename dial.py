import cv2
import math
import numpy as np

_RED_LOW = ((0, 30, 10), (15, 255,255))
_RED_HIGH = ((165, 30, 10), (179, 255,255))
_DIAL_COUNT = 4
_DIAL_SCALE_ANGLE = 360 / 10

def _distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
 
def _get_extremes(contour):
    return [tuple(contour[contour[:, :, 0].argmin()][0]),
        tuple(contour[contour[:, :, 0].argmax()][0]),
        tuple(contour[contour[:, :, 1].argmin()][0]),
        tuple(contour[contour[:, :, 1].argmax()][0])]

def _mask(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask_low = cv2.inRange(hsv_image, (0, 30, 10), (15, 255,255))
    mask_high = cv2.inRange(hsv_image, (165, 30, 10), (179, 255,255))
    mask_full = mask_low + mask_high > 0
    masked = np.zeros_like(image, np.uint8)
    masked[mask_full] = image[mask_full]
    return masked

def _threshold(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold = cv2.threshold(gray, 0, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return threshold

def _contours(image):
    im2, contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Sort contours by size and take the biggest
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:_DIAL_COUNT]
    # Sort contours reversed by x axis coordinate
    contours = sorted(contours, key = lambda x: x[0][0][0], reverse = True)
    return contours

def _contour_to_value(contour):
    # compute the "center of mass" of the contour
    M = cv2.moments(contour)
    center_x = int(M["m10"] / M["m00"])
    center_y = int(M["m01"] / M["m00"])
    moment_point = tuple((center_x, center_y))
    
    # Calculate coordinate extremes from contour
    extremes = _get_extremes(contour)
    
    # Calculate extreme point distances from the center
    distances = list(map(lambda x: _distance(moment_point, x), extremes))
    direction_point = extremes[distances.index(max(distances))]
    
    raw_angle = math.degrees(math.atan2(moment_point[0] - direction_point[0], moment_point[1] - direction_point[1]))
    angle = raw_angle if raw_angle > 0 else 360 + raw_angle
    angle = 360 - angle
    
    dial_value = angle / _DIAL_SCALE_ANGLE
    return int(dial_value)

def _get_dials(image, verbose):
    masked = _mask(image)
    if verbose:
        cv2.imshow("Masked image", masked)
        cv2.waitKey(0)
    threshold = _threshold(masked)
    if verbose:
        cv2.imshow("Threshold", threshold)
        cv2.waitKey(0)
    contours = _contours(threshold)
    if verbose:
        contours_image = image.copy()
        cv2.drawContours(contours_image, contours, -1, (0, 255, 0), 1)
        cv2.imshow("Contours", contours_image)
        cv2.waitKey(0)
    values = list(map(lambda c: _contour_to_value(c), contours))
    if verbose:
        print(values)
    
# Public meter reading without verbose output
def get_litres(image):
    handle_image(image, False)
    return 1.1

if __name__ == "__main__":
    import argparse
        
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
        help="path to dial image")
    ap.add_argument("-v", "--verbose", action='store_true', help="verbose GUI debugging")
    
    args = vars(ap.parse_args())

    # load the example image and convert it to grayscale
    image = cv2.imread(args["image"])

    orig = image.copy()

    if args["verbose"]:
        cv2.imshow("Original", orig)
        cv2.waitKey(0)

    dials = _get_dials(image, args["verbose"])


