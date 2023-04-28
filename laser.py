import numpy as np

"""
Represente le cercle du laser
"""
class laser:
    def __init__(self):
        self.rayon = 10

        self.precision = 0

        self.number_step = 10
        self.step_angle = 2 * np.pi / self.number_step
        self.step_radius = self.rayon / self.number_step
        self.current_pos_polar = [self.step_radius, 0] # [mod, angle]
        self.next_pos_cartesian =  [0, 0]   # holds the next position to send relative to the current position
        self.center_cartesian = [0, 0]
        pass

    
    def polar_to_cartesian(self, mod: float, angle: float) -> list[float]:
        """
        This function translate polar coordinate to cartesian coordinate
        Return a List: [x, y]
        """
        x = mod * np.sin(angle) + self.center_cartesian[0]
        y = mod * np.cos(angle) + self.center_cartesian[1]
        return [float(x), float(y)]


    def new_pos(self) -> None:
        """
        This function compute the next wanted x and y offset \n
        for the next position 
        Stores it in the member "next_pos_cartesian"
        """
        old_angle = self.current_pos_polar[1]
        old_mod = self.current_pos_polar[0]

        new_angle = old_angle + self.step_angle 
        new_mod = old_mod
        if (self.current_pos_polar[1] >= np.pi * 2):
            new_mod += self.step_radius
            new_angle = 0
            pass
        
        old_x, old_y = self.polar_to_cartesian(old_mod, old_angle)
        new_x, new_y = self.polar_to_cartesian(new_mod, new_angle)

        self.next_pos_cartesian = [round(new_x-old_x, 2), round(new_y-old_y, 2)]
        self.current_pos_polar = [new_mod, new_angle]

        pass


    def set_center(self, xy: tuple[int, int]) -> None:
        """
        This function set the center of the laser in pixel coordinate
        """
        self.center_cartesian = xy
        pass


    def reset_polar_coordinate(self) -> None:
        """This function reset the angle and module of the laser"""
        self.current_pos_polar = [self.step_radius, 0]
        pass


    def reset(self) -> None:
        """This function reset all the value and configuration of the object"""
        self.reset_polar_coordinate()
        self.center_cartesian = (0, 0)

    # TEMP
    """
    Met a jour les valeurs actuelles de la position du laser
    """
    def deplacer(self,context): 
        height,width,depth = np.shape(context)
        visible = False
        while not visible :
            x,y = self.getPos()

            self.centerCircle[0] += self.pas_rayon
            if self.centerCircle[1] >= 2*np.pi*2:
                self.centerCircle[1] = 0
            else :
                self.centerCircle[1] += self.pas_angle

            if x<width and x>0 and y<height and y>0:
                visible = True
            


    # TEMP
    def updateCenter(self,newX,newY):
        print("~~laser centré : ",newX," ",newY," ~~\n")
        if [[newX,newY]==self.start] :
            self.precision += 1
            print("centre trouvé", self.precision," fois")
        else :
            self.precision = 0
        self.start = [newX,newY]
        self.centerCircle = [0,0]
        pass
    pass