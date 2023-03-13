import cv2
import numpy as np
import tkinter as tk 
import time

import Pointeur_laser as Laser
import Panneau
import discovered_sign

taille_ecran = 500


def detectCircle(image, min_radius, max_radius, min_distance, threshold=100):
    """
    Detect all circle in the given image and return a list of point representing them
    Point structure are as follow: [x_center, y_center, radius]
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.blur(gray, (3, 3))
    
    detected_circles = cv2.HoughCircles(gray_blurred, 
                   cv2.HOUGH_GRADIENT, 1, min_distance, param1 = 10,
               param2 = threshold, minRadius = min_radius, maxRadius = max_radius)
    
    if detected_circles is not None:
        # Convert the circle parameters a, b and r to integers.
        detected_circles = np.uint16(np.around(detected_circles))
        return detected_circles[0, :]
    return []



def main():
    paused = False
    plan =  np.zeros((taille_ecran,taille_ecran,3), np.uint8)
    laser = Laser.Pointeur_laser(100,100,10)
    panneau = Panneau.Panneau(150,150,30)
    decouvert = discovered_sign.Panneau_decouvert(taille_ecran,taille_ecran)

    while True :
        if paused == False :
            plan = np.zeros((taille_ecran,taille_ecran,3), np.uint8)
            laser.deplacer(plan)
            cv2.circle(plan,panneau.getPos(),panneau.rayon,(150,0,0),-1)
            cv2.circle(plan,laser.getPos(),laser.rayon,(0,0,255),-1)
            cv2.imshow("plan",plan)

            panneau.reflechit_lumiere(plan,decouvert.matLumiere)
            cv2.imshow("panneau découvert",decouvert.matLumiere)
            

        if cv2.waitKey(1) == 27: 
            break  # esc to quit
        if cv2.waitKey(1) == 13:
            paused = not paused
            laser.precision = 0

        if laser.precision < 3 :
            if laser.centerCircle[1]==0: 
                print("\n ~~avant appel fonction cercles~~\n ") #draw circles
                newX , newY, detected=  DetectCircle(decouvert.matLumiere)
                if detected :
                    laser.updateCenter(newX,newY)
        else:
            paused = True
            d = np.sqrt((laser.start[0]-panneau.center[0])**2+(laser.start[1]-panneau.center[1])**2)
            print("centre du panneau trouvé à ",d," pixels près")
    pass 

if __name__ == '__main__':
    main()