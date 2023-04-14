from tkinter import *
from tkinter import ttk
import threading
import time
import PIL.Image
import PIL.ImageTk
import cv2
import ctypes

import cam
import circles
import discovered_sign
import laser

ctypes.windll.shcore.SetProcessDpiAwareness(2)

class UI:
    def __init__(self, circle_threshold, path_to_dll) -> None:
        self.widgets = {}                                   # holds all the widgets of the window
        self.thread = [None, None]                          # list of thread for the computation
        self.image_to_draw = [None, None, None]             # 0: img from cam, 1: img with circle, 2: light detection

        self.circle = circles.Circle(circle_threshold)      # Circle object, hold parameter for the detection
        self.is_camera_on = False                                   # current state of the webcam
        self.is_reflect_on = False                                   # current state of the reflection's detection
        self.list_choice_camera = ["None", "Imaging Source camera", "From File"] # hold every possible image source 
        self.path_to_dll = path_to_dll
        self.camera = None                                  # Camera object, see cam.py, only initialized when selecting a camera
        self.reflection = discovered_sign.DiscoveredSign()  # DiscoveredSign object, only initialized when the reflection detection starts
        self.laser = laser.laser()
        self.laser_position_to_send = [0, 0]


        self.root = Tk()
        self.root.geometry("1600x900")
        pass


    def setup(self):
        self.constructFrame()
        pass

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.mainloop()
        pass

    def close(self):
        """This function makes sure everything is well setup to be correctly closed"""
        print("Closing the app...")
        self.is_camera_on = False
        self.is_reflect_on = False
        self.root.destroy()
        print("Program closed")

    def constructFrame(self):
        """
        Create and place every widget of the window
        Using a dictionnary to make it easier to access every widget from any point of the program
        """
        width = 20
        height = 1

        # The frame is split in two part
        self.widgets["left_frame"] = left_frame = ttk.Frame(self.root)
        self.widgets["right_frame"] = right_frame = ttk.Frame(self.root)

        self.widgets["start_camera"] = Button(left_frame, text="Start Camera", command=self.startStopCamera, width=width, height=height)
        
        scale_threshold = Scale(left_frame, from_=1, to=100, orient=HORIZONTAL, 
                             label="Threshold for the circle detection", length=250,
                             command=self.updateCircleThreshold)
        scale_threshold.set(self.circle.threshold)
        self.widgets["scale_threshold"] = scale_threshold
        
        self.widgets["center_reflection"] = Label(right_frame, text="center : [0, 0]")

        self.widgets["set_camera"] = Button(left_frame, text="Set camera", command=self.set_camera, width=width, height=height)

        self.widgets["start_reflection"] = Button(right_frame, text="Start Reflection", command=self.startStopReflection, width=width, height=height)
        self.widgets["reset_reflection"] = Button(right_frame, text="Reset Reflection", command=self.reflection.resetLight, width=width, height=height)

        scale_threshold_light = Scale(right_frame, from_=1, to=100, orient=HORIZONTAL, 
                             label="Threshold for the light detection", length=250,
                             command=self.reflection.set_threshold)
        scale_threshold_light.set(self.reflection.threshold_intensity)
        self.widgets["scale_threshold_light"] = scale_threshold_light


        # packing all the top widget to the frame
        self.widgets["set_camera"].pack()
        self.widgets["start_camera"].pack()
        self.widgets["scale_threshold"].pack()

        self.widgets["start_reflection"].pack()
        self.widgets["reset_reflection"].pack()
        self.widgets["scale_threshold_light"].pack()
        self.widgets["center_reflection"].pack()



        # ==================================
        # Bottom side for the image and video

        self.widgets["image_output"] = Label(left_frame)
        self.widgets["image_output_bis"] = Label(right_frame)

        self.widgets["image_output"].pack(fill=BOTH, expand=True, side=BOTTOM)
        self.widgets["image_output_bis"].pack(fill=BOTH, expand=True, side=BOTTOM)

        left_frame.pack(fill=BOTH, expand=True, side=LEFT)
        right_frame.pack(fill=BOTH, expand=True, side=RIGHT)

        pass


    # Managing State of the camera =======================================
    def camera_start(self):
        self.is_camera_on = True
        self.camera.startCamera()
        self.thread[0] = threading.Thread(target=self.compute_circle)
        self.thread[0].start()
        self.camera_change_button_prefix("Stop")

        print("Camera started")
        pass
    
    def camera_stop(self):
        self.is_camera_on = False
        self.camera.stopCamera()
        self.camera_change_button_prefix("Start")

        self.reflection_stop()
        print("Camera (and reflection) stopped")
        pass

    def camera_change_button_prefix(self, new_prefix: str):
        self.widgets["start_camera"].configure(text=(new_prefix + " Camera"))
        pass   

    def startStopCamera(self):
        """Choosing the action to make depending of the state of the camera"""
        if self.is_camera_on:
            # stoping the camera (and the reflection)
            self.camera_stop()
        else:
            # starting the camera
            self.camera_start()

        self.update_all_image()
        pass
    # ====================================================================

    # Managing state of the reflection ===================================
    def reflection_start(self):
        self.is_reflect_on = True
        
        self.reflection.resetLight()
        self.thread[1] = threading.Thread(target=self.compute_reflection)
        self.thread[1].start()

        self.reflection_change_button_prefix("Stop")
        print("Reflection started")
        pass

    def reflection_stop(self):
        self.is_reflect_on = False
        self.reflection_change_button_prefix("Start")
        print("Reflection stopped")
        pass

    def reflection_change_button_prefix(self, new_prefix: str):
        self.widgets["start_reflection"].configure(text=(new_prefix + " Reflection"))
        pass    

    def startStopReflection(self):
        """
        Choosing the action to make depending of the state of the reflection\n
        The camera must be started before calling this function
        """
        if not self.is_camera_on and not self.is_reflect_on:
            # Stop the function here because condition are not respected
            print("Camera must be ON")
            return

        if self.is_reflect_on:
            self.reflection_stop()
        else:
            self.reflection_start()
        pass
    # ====================================================================

    def center_update(self):
        center = self.widgets["center_reflection"]
        coord = self.reflection.getCenter()
        coord = "Center : [" + str(coord[0]) + ", " + str(coord[1]) + "]"
        center.configure(text=coord)


    def update_all_image(self):
        """
        This function will update all the image to draw on the tkinter window
        """
        if self.is_camera_on:
            image_output = self.widgets["image_output"]
            image_output_bis = self.widgets["image_output_bis"]
 
            # Draw the second image -> live feed
            image = self.image_to_draw[1]
            if image is not None:   
                image = self.ImageOpencvToTkinter(image)
            image_output.imgtk = image
            image_output.configure(image=image)

            # Draw the third image -> reflection
            image = self.image_to_draw[2]
            if image is not None:
                image = self.ImageOpencvToTkinter(image)
            image_output_bis.configure(image=image)
            
            self.center_update()
            self.next_movement_computing()
            image_output.after(20, self.update_all_image)
        pass

    def compute_circle(self):
        """
        This function access the camera live feed to get 1 frame, compute the circle with the circle object
        then draw the circle on the image
        Save the result image in the first slot of the "image_to_draw" attribute
        """
        while self.is_camera_on:
            img = self.camera.getImage()

            list_point = self.circle.detectCircle(img)
            original_image = circles.drawCircle(img, list_point)
            self.image_to_draw[0] = original_image

            self.image_to_draw[1] = img

            time.sleep(0.02)
        return
    
    def compute_reflection(self):
        """
        This function uses the DiscovredSign object to compute the reflection between 2 frames
        Save the result image in the second slot of the "image_to_draw" attribute
        """
        while self.is_camera_on and self.is_reflect_on:   
            image_input = self.image_to_draw[0]

            reflection = self.reflection.detectReflexion(image_input)
            self.reflection.addNewReflection(reflection)

            self.image_to_draw[2] = self.reflection.light_map
        return

    def updateImageLive(self):
        """
        This function takes image from the video feed and output it on the widget "image_output"
        Call itself every 20ms to get a constant video feed
        It also detect circle with the threshold chosen with the "scale_threshold" widget
        """
        image_output = self.widgets["image_output"]
        if self.is_camera_on:
            img = self.camera.getImage()

            list_point = self.circle.detectCircle(img)
            img = circles.drawCircle(img, list_point)

            img = self.ImageOpencvToTkinter(img)
            # update image on tkinter window
            image_output.imgtk = img
            image_output.configure(image=img)
            image_output.after(20, self.updateImageLive)
            pass
        else:
            image_output.imgtk = None
            image_output.configure(image=None)
        pass

    def updateImageReflection(self):
        """
        This function takes image from the video feed and output it on the widget "image_output2"
        Call itself every 20ms to get a constant video feed
        """
        image_output_bis = self.widgets["image_output_bis"]
        
        image_input = self.camera.getImage()

        reflection = self.reflection.detectReflexion(image_input)
        self.reflection.addNewReflection(reflection)

        img = self.ImageOpencvToTkinter(self.reflection.light_map)
        # update image on tkinter window
        image_output_bis.imgtk = img
        image_output_bis.configure(image=img)

        image_output_bis.after(100, self.updateImageReflection)
        pass

    def updateCircleThreshold(self, new_value):
        self.circle.threshold = int(new_value)
        pass
    pass


    def set_camera(self):

        self.camera = cam.Camera(self.path_to_dll)
        height, width = self.camera.getImageSize()
        self.reflection.initialization(height, width)
        pass

    def ImageOpencvToTkinter(self, img):
        """
        convert opencv image format to a tkinter format
        """
        width = int(self.root.winfo_width()*0.45)
        height = int(self.root.winfo_height()*0.45)
        img_resized = cv2.resize(img, (width, height))
        img = PIL.Image.fromarray(img_resized)
        img = PIL.ImageTk.PhotoImage(img)
        return img
    
    def next_movement_computing(self) -> None:
        """
        This function choose between continuing the normal detection cycle\n
        or moving to the detected area
        """
        self.laser.new_pos()

        if (self.reflection.number_of_white_pixel  <  self.reflection.threshold_detected):
            self.laser_position_to_send = self.laser.current_pos_polar
        else:
            self.laser_position_to_send = self.reflection.center
            self.laser.set_center( self.reflection.center )
            self.laser.reset_polar_coordinate()
            pass
        pass



ui = UI(100, "./Lib/site-packages/tisgrabber/samples/tisgrabber_x64.dll")
ui.setup()



ui.run()