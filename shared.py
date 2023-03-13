import cv2
import numpy as np

import Panneau

"""
import Pointeur_laser as laser
import Panneau
import Panneau_decouvert
"""

def Createimgcircles(image, seuil):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.blur(gray, (3, 3))
    detected_circles = cv2.HoughCircles(gray_blurred, 
                    cv2.HOUGH_GRADIENT, 1, 20, param1 = 10,
                    param2 = seuil, minRadius = 1, maxRadius = 300)
    if detected_circles is not None:

        # Convert the circle parameters a, b and r to integers.
        detected_circles = np.uint16(np.around(detected_circles))
    
        for pt in detected_circles[0, :]:
            a, b, r = pt[0], pt[1], pt[2]
    
            # Draw the circumference of the circle.
            cv2.circle(image, (a, b), r, (0, 255, 0), 2)
    
            # Draw a small circle (of radius 1) to show the center.
            cv2.circle(image, (a, b), 1, (0, 0, 255), 3)
    return detected_circles


def show_webcam(cam):
    paused = False
    while True:
        ret_val, img = cam.read()

        if paused:
            pt = detected_circles[0, :]
            if pt.any():
                pt = pt[0]
                panneau = Panneau.Panneau(pt[0], pt[1], pt[2])
                cv2.circle(img, (pt[0], pt[1]), pt[2], (0, 255, 0), 2)
                cv2.circle(img, (pt[0], pt[1]), 1, (0, 255, 0), 2)
        else:
            detected_circles = Createimgcircles(img, 100)
        cv2.imshow('my webcam', img) 

        if cv2.waitKey(1) == 27: 
            break  # esc to quit
        if cv2.waitKey(1) == 13:
            paused = not paused
    cv2.destroyAllWindows()

def main():
    #cam = cv2.VideoCapture(0)
    #show_webcam(cam)
    img = cv2.imread('image_lumiere.jpg',-1)
    print(img.dtype)
    img = img.astype()
    Createimgcircles(img,30)
    while True:
        cv2.imshow('image traité',img)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit

if __name__ == '__main__':
    main()