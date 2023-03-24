import cv2
import numpy as np
import tkinter as tk 

class Circle:
    """This class is used to hold and configure the parameter for the Circle detection"""
    def __init__(self, th) -> None:
        self.min_radius = 0
        self.max_radius = 300
        self.min_distance = 100
        self.threshold = th
        pass

    def detectCircle(self, image):
        """
        Detect every circle in the given image and return a list of point representing them
        Parameter of the detection are held in the object itself

        Arguments:
        image: Mat
        
        Returns:
        [[x_center, y_center, radius], ... ]
        """
        #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = image
        gray_blurred = cv2.blur(gray, (3, 3))
        
        detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 
                                            self.min_distance, 
                                            param1 = 100, param2 = self.threshold, 
                                            minRadius = self.min_radius, maxRadius = self.max_radius)
        
        if detected_circles is not None:
            # Convert the circle parameters a, b and r to integers.
            detected_circles = np.uint16(np.around(detected_circles))
            return detected_circles[0, :]
        return []


def drawCircle(image, list_point):
    """
    Draw circle defined by the point in the given list on the image
    Return the original image
    
    Parameters:
    image: Mat
    list_point: [[x_center, y_center, radius], ...]
    
    Return:
    image: Mat
    """
    original_image = np.copy(image)
    for point in list_point:
        cv2.circle(image, (point[0], point[1]), point[2], (0, 0, 255), 3)
    return original_image