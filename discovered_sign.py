import cv2
import numpy as np
"""
Represente les parties du panneau decouvert
La matrice qui stoque les coordonnees est de la forme: lumiereMat[y][x]
"""
class DiscoveredSign:
    def __init__(self,inputW,inputH):
        self.width = inputW
        self.height = inputH
        self.center = [0, 0]
        self.light_map = None

        self.threshold_intensity = 150
        
        self.saved_image = None

        self.resetLight()
        pass

    def getCenter(self):
        return self.center[0], self.center[1]
    
    def detectReflexion(self, image1):
        """
        This function is comparing the given image and the stored one, these image should be almost identical image (ex: 2 successive frames of a video)
        Its goal is to detect a new high intensity region in the second image which would correspond to the reflection against the CornerCube
        or the road sign used
        It does that by applying a threshold an both image to eliminate low intensity region and then substract one image to the other
        If a new high intensity region has appeared between the image, it will be the only region of the image where pixel are not 0

        Parameters:
        image1: Mat
        image2: Mat
        """
        # the second image is loaded to make computation
        image2 = self.saved_image

        if image2 is None:
            # for the first frame, we only have one image so we must be sure there no problem
            image2 = image1
            pass

        # the saved image takes the new image input for the next call of the function
        self.saved_image = image1

        new_mat = cv2.subtract(image2, image1)
        th, new_mat = cv2.threshold(new_mat, self.threshold_intensity, 255, cv2.THRESH_BINARY)
        return new_mat
    
    def addNewReflection(self, reflected):
        """
        This function will add region of light into the "light_map" matrix

        Parameter:
        reflected: Mat - should be mostly 0
        """
        self.light_map = cv2.add(self.light_map, reflected)
        pass

    def resetLight(self):
        self.light_map = np.zeros((self.width, self.height,3),np.uint8)
    pass


def main():
    im1 = cv2.imread("IC Camera/1.bmp")
    im2 = cv2.imread("IC Camera/2.bmp")
    im3 = cv2.imread("IC Camera/3.bmp")
    im4 = cv2.imread("IC Camera/4.bmp")
    d = DiscoveredSign(640, 480)
    
    m = d.detectReflexion(im1, im2)
    d.addNewReflection(m)
    cv2.imshow("Julo", d.light_map)
    cv2.waitKey(2000)

    m = d.detectReflexion(im3, im4)
    d.addNewReflection(m) 
    cv2.imshow("Julo", d.light_map)
    cv2.waitKey(2000)
    pass

if __name__ == '__main__':
    main()    
    pass