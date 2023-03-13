import numpy as np
"""
Represente le cercle du laser
"""
class Pointeur_laser :
    def __init__(self, posX, posY, input_r):
        self.start = [posX, posY]
        self.rayon = input_r
        self.centerCircle = [0,0] #coordonnées polaires rayon / angle

        self.precision = 0

        self.nb_pas = 50
        self.pas_angle = 2 * np.pi / self.nb_pas
        self.pas_rayon = 2 * self.rayon / self.nb_pas


        pass

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
            

    """
    Calcul la position en x, y du centre du laser
    """
    def getPos(self):
        x = self.centerCircle[0] * np.cos( self.centerCircle[1] )
        y = -self.centerCircle[0] * np.sin( self.centerCircle[1] )
        actualPos = [int(self.start[0]+x),int(self.start[1]+y)]
        return actualPos

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