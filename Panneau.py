import numpy as np
"""
Represente le panneau et ses caracteristique
"""
class Panneau:
    def __init__(self,inputX,inputY,inputR):
        self.center = [inputX,inputY]
        self.rayon = inputR
        pass

    def getPos(self):
        return self.center
        
    def getrayon(self):
        return self.rayon

    

    def reflechit_lumiere(self,mat_laser,mat_lumiere):
        
        debutX = self.center[0]-self.rayon
        debutY = self.center[1]-self.rayon

        for x in range(debutX , debutX+2*self.rayon) :
            for y in range(debutY , debutY+2*self.rayon):
                if mat_laser[y][x][2] == 255:
                    dX = self.center[0] - x
                    dY = self.center[1] - y
                    dR = np.sqrt(dX**2+dY**2)
                    if dR <= self.rayon :
                        #print("~~lumière détectée ~~\n")

                        mat_lumiere[y][x] = (255,255,255)
        pass
    pass