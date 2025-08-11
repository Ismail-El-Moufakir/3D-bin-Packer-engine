import numpy as np
# class for volume units/position
class Vector3:
    def  __init__(self,x:int = 0,y:int = 0,z:int =0): 
        self.x = x
        self.y = y
        self.z = z
    def volume(self):
        return self.x*self.y*self.z
#item class
class Item:
    def __init__(self,id : str,dim: Vector3,weight:float,rotatable:bool = True,order:int = 0,group_id:int = 0):
        self.id = id
        self.dim = dim
        self.weight = weight
        self.group_id = group_id
        self.rotatable = rotatable
        self.order = order



#class bin
class Bin:
    def __init__(self,id:int,max_weight:int,W:int,L:int,H:int):
        self.id = id
        self.max_weight = max_weight
        self.W = W
        self.L = L
        self.H = H
        self.used_weight = 0

        
# placement class
class Placement:
    def __init__(self,item_id:str = None, bin_id:int = None, position:Vector3 = None, dimensions:Vector3 = None):
        self.item_id = item_id
        self.bin_id = bin_id
        self.position = position
        self.dimensions = dimensions

# rect class
class Rect:
    def __init__(self,x:int,y:int,w:int,h:int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h