import cv2
import numpy as np
import ctypes
import tisgrabber as tis

import laser as Laser
import Panneau
import discovered_sign

taille_ecran = 500

class Camera:
    def __init__(self, path_to_dll) -> None:
        self.ic = ctypes.cdll.LoadLibrary(path_to_dll)      # loading the dll file
        self.ic.IC_InitLibrary(0)                           # setup IC object
        tis.declareFunctions(self.ic)                       
        self.hGrabber = tis.openDevice(self.ic)             # setup hGrabber, contain camera info
        pass

    def setCamera(self):
        self.hGrabber = self.ic.IC_ShowDeviceSelectionDialog(None)
        pass
    
    def startCamera(self):
        self.ic.IC_StartLive(self.hGrabber, 0)
    
    def stopCamera(self):
        self.ic.IC_StopLive(self.hGrabber)
    
    def getImage(self):
        """
        This function captures an image from the video feed
        Converts it to a format usable in openCV by using Numpy
        """
        if self.ic.IC_SnapImage(self.hGrabber, 2000) == tis.IC_SUCCESS:
            # Declare variables of image description
            # This library uses pointer in python which need to be declared
            Width = ctypes.c_long()
            Height = ctypes.c_long()
            BitsPerPixel = ctypes.c_int()
            colorformat = ctypes.c_int()

            # Query the values of image description
            self.ic.IC_GetImageDescription(self.hGrabber, Width, Height, BitsPerPixel, colorformat)

            # Calculate the buffer size
            bpp = int(BitsPerPixel.value / 8.0)
            buffer_size = Width.value * Height.value * BitsPerPixel.value

            # Get the image data
            imagePtr = self.ic.IC_GetImagePtr(self.hGrabber)
 
            imagedata = ctypes.cast(imagePtr, ctypes.POINTER(ctypes.c_ubyte * buffer_size))

            # Create the numpy array
            image = np.ndarray(buffer=imagedata.contents,
                                dtype=np.uint8,
                                shape=(Height.value, Width.value, bpp))
            image = cv2.flip(image, 0)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return image
        return None

    def getImageSize(self):
        """
        This function return the current size of the image
        """
        width = self.ic.IC_GetVideoFormatWidth(self.hGrabber)
        height = self.ic.IC_GetVideoFormatHeight(self.hGrabber)
        return height, width

def DetectCircle(image,seuil):
    """
    This function detect circle in the given image with a threshold
    Return a Point describing the center point (with a radius of 1 to represent only a point) 
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.blur(gray, (3, 3))
    
    detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 
                                        20, param1 = 10, param2 = seuil, 
                                        minRadius = 1, maxRadius = 300)
    
    if detected_circles is not None:
        # Convert the circle parameters a, b and r to integers.
        detected_circles = np.uint16(np.around(detected_circles))

        a, b = detected_circles[0][0][0], detected_circles[0][0][1]

        print("je detecte un cercle")

        return a,b,1
    else:
        return 0,0,0



def main():
    cam = cv2.VideoCapture(0) 
    plan =  np.zeros((taille_ecran,taille_ecran,3), np.uint8)
    laser = Laser.Pointeur_laser(100,100,10)
    decouvert = discovered_sign.Panneau_decouvert(taille_ecran,taille_ecran)
    paused = False
    recherche = False

    while True :
        if paused == False:
            if recherche == True:
                
                plan = np.zeros((taille_ecran,taille_ecran,3), np.uint8)
                laser.deplacer(plan)
                cv2.circle(plan,panneau.getPos(),panneau.rayon,(150,0,0),-1)
                cv2.circle(plan,laser.getPos(),laser.rayon,(0,0,255),-1)
                cv2.circle(cam_img,laser.getPos(),laser.rayon,(0,0,255),-1)
                

                panneau.reflechit_lumiere(plan,decouvert.matLumiere)
                
                
                if laser.precision < 3 :
                    if laser.centerCircle[1]==0: 
                        print("\n ~~avant appel fonction cercles~~\n ") #draw circles
                        newX , newY, detected=  DetectCircle(decouvert.matLumiere,20)
                        if detected :
                            laser.updateCenter(newX,newY)
                else:
                    paused = True
                    d = np.sqrt((laser.start[0]-panneau.center[0])**2+(laser.start[1]-panneau.center[1])**2)
                    print("centre du panneau trouvé à ",d," pixels près")

            ret_val,cam_img = cam.read()
            cv2.imshow("cam",cam_img)
            cv2.imshow("panneau découvert",decouvert.matLumiere)

        if cv2.waitKey(1) == 27: # esc to quit
            break 
        if cv2.waitKey(1) == 13: #entrée pour pause
            paused = not paused
        if cv2.waitKey(1) == 32: #barre espace pour lock la pos d'un panneau
            
            laser.precision = 0
            newX , newY, detected=  DetectCircle(decouvert.matLumiere,50)
            recherche = False
            if detected :
                panneau = Panneau.Panneau(newX,newY,30)
                recherche = True  
                print("cocou")
    pass

if __name__ == '__main__':
    main()