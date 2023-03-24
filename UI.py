from tkinter import *
from tkinter import ttk
import threading
import time
import PIL.Image
import PIL.ImageTk
import cv2

import cam
import circles
import discovered_sign

class UI:
    def __init__(self, circle_threshold, path_to_dll) -> None:
        self.widgets = {}                                   # holds all the widgets of the window
        self.thread = [None, None]                          # list of thread for the computation
        self.play = False                                   # current state of the webcam
        self.list_choice_camera = ["None", "Imaging Source camera", "From File"] # hold every possible image source 
        self.path_to_dll = path_to_dll
        self.camera = None                                  # Camera object, see cam.py, only initialized when selecting a camera
        self.reflection = discovered_sign.DiscoveredSign()  # DiscoveredSign object, only initialized when the reflection detection starts
        self.circle = circles.Circle(circle_threshold)      # Circle object, hold parameter for the detection
        self.image_to_draw = [None, None, None]             # 0: img from cam, 1: img with circle, 2: light detection
        self.i = 0 # TEMP

        self.root = Tk()
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
        self.play = 0
        self.root.destroy()
        print("Program closed")

    def constructFrame(self):
        """
        Create and place every widget of the window
        Using a dictionnary to make it easier to access every widget from any point of the program
        """
        # left side where all the button are
        self.widgets["left_frame"] = left_frame =  ttk.Frame(self.root)

        self.widgets["start_camera"] = Button(left_frame, text="Start Camera", command=self.startStopCamera)
        
        scale_threshold = Scale(left_frame, from_=1, to=100, orient=HORIZONTAL, 
                             label="Select the threshold value for the circle detection", length=250,
                             command=self.updateCircleThreshold)
        scale_threshold.set(self.circle.threshold)
        self.widgets["scale_threshold"] = scale_threshold
        
        self.widgets["change_camera456456"] = Button(left_frame, text="4564 camera" , command=self.reflection.find_center).pack()
        self.widgets["change_camera"] = ttk.Combobox(left_frame, values=self.list_choice_camera)
        self.widgets["change_camera"].current(0)
        self.widgets["change_camera"].bind("<<ComboboxSelected>>", self.choose_camera)
        
        self.widgets["start_reflection"] = Button(left_frame, text="Start Reflection", command=self.startResetReflection)

        self.widgets["reset_reflection"] = Button(left_frame, text="Reset Reflection", command=self.reflection.resetLight)

        scale_threshold_light = Scale(left_frame, from_=1, to=100, orient=HORIZONTAL, 
                             label="Select the threshold value for the light detection", length=250,
                             command=self.reflection.set_threshold)
        scale_threshold.set(self.reflection.threshold_intensity)
        self.widgets["scale_threshold_light"] = scale_threshold_light


        # packing all the left widget to the frame
        self.widgets["change_camera"].pack(fill=X)

        
        self.widgets["start_camera"].pack(fill=X)
        self.widgets["start_reflection"].pack(fill=X)
        self.widgets["reset_reflection"].pack(fill=X)

        self.widgets["scale_threshold"].pack(fill=X)
        self.widgets["scale_threshold_light"].pack(fill=X)


        # ==================================
        # right side for the image and video
        self.widgets["right_frame"] = right_frame = Frame(self.root, width=300, height=300)


        scale = 120
        width = 4*scale
        height = 3*scale
        self.widgets["image_output"] = Label(right_frame)
        self.widgets["image_output_bis"] = Label(right_frame)

        self.widgets["image_output"].pack(fill=BOTH, expand=True, side=LEFT)
        self.widgets["image_output_bis"].pack(fill=BOTH, expand=True, side=LEFT)


        left_frame.pack(fill=BOTH, expand=True, side=TOP)
        right_frame.pack(fill=BOTH, expand=True, side=BOTTOM)

        pass

    def startStopCamera(self):
        """
        Choosing the action to make and the text to show on the button depending of the state of the camera
        If it is already running, it is stopped then the button is labeled "Start Camera"
        If it is not, it is started and the button is labeled "Stop Camera"
        """
        if (self.play):
            # stoping the camera
            self.camera.stopCamera()
            label = "Start "
        else:
            # starting the camera
            self.camera.startCamera()
            label = "Stop "
            self.thread[0] = threading.Thread(target=self.compute_circle)
            self.thread[0].start()
        self.widgets["start_camera"].configure(text=(label + "Camera"))
        self.play = not self.play

        self.update_all_image()
        # self.updateImageLive()
        pass

    def startResetReflection(self):
        """
        This function declare the DiscorveredSign object then starts the detection frame by frame
        The camera must be started before calling this function
        """
        if self.play:
            # self.updateImageReflection()
            self.reflection.resetLight()
            self.thread[1] = threading.Thread(target=self.compute_reflection)
            self.thread[1].start()
        pass

    def update_all_image(self):
        """
        This function will update all the image to draw on the tkinter window
        """
        if self.play:
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
            image_output_bis.imgtk = image
            image_output_bis.configure(image=image)
            
            image_output.after(20, self.update_all_image)
        pass

    def compute_circle(self):
        """
        This function access the camera live feed to get 1 frame, compute the circle with the circle object
        then draw the circle on the image
        Save the result image in the first slot of the "image_to_draw" attribute
        """
        time.sleep(1)
        while self.play:
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
        while self.play:            
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
        if self.play:
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


    # TEMP
    def choose_camera(self, event):
        selection = self.widgets["change_camera"].get()
        if (selection == self.list_choice_camera[1]): # imaging source camera
            self.camera = cam.Camera(self.path_to_dll)

            height, width = self.camera.getImageSize()
            self.reflection.initialization(height, width)
            # if cancel button has been pressed, bugs WILL happened
            pass
        elif (selection == self.list_choice_camera[2]): # from image
            self.updateImageBis()
            pass
        pass

    # TEMP
    def updateImageBis(self):
        self.play = True
        image_output = self.widgets["image_output"]
        list_image = [cv2.imread("IC Camera/1.bmp"), 
                      cv2.imread("IC Camera/2.bmp"), 
                      cv2.imread("IC Camera/3.bmp"), 
                      cv2.imread("IC Camera/4.bmp"),
                      cv2.imread("IC Camera/5.bmp")]
        if self.play:
            img = list_image[self.i]
            self.i += 1
            if (self.i == 2):
                self.i = 0
            
            img = self.ImageOpencvToTkinter(img)
            # update image on tkinter window
            image_output.imgtk = img
            image_output.configure(image=img)
            image_output.after(2000, self.updateImageBis)
            pass
        else:
            image_output.imgtk = None
            image_output.configure(image=None)
        pass


    def ImageOpencvToTkinter(self, img):
        """
        convert opencv image format to a tkinter format
        """
        # convertion
        img = PIL.Image.fromarray(img)
        img = PIL.ImageTk.PhotoImage(img)
        return img


ui = UI(100, "./Lib/site-packages/tisgrabber/samples/tisgrabber_x64.dll")
ui.setup()



ui.run()