from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,Counter
from OpenDriveMap.planView import Direct
class CornerLocal:
    def __init__(self,node):
        self.u=float(node.getAttribute('u'))
        self.v=float(node.getAttribute('v'))
        self.z=float(node.getAttribute('z'))
    def getDirect(self,referenceDirect):
        referenceDirect.offset(self.u)
        referenceDirect.forward(self.v)
        return referenceDirect
    
class Outline:
    def __init__(self,node,object):
        self.object=object
        self.cornerLocals=[]
        cornerLocals=node.getElementsByTagName('cornerLocal')
        for cornerLocal in cornerLocals:
            self.cornerLocals.append(CornerLocal(cornerLocal))
            
class Object:
    def __init__(self,node):
        self.id=node.getAttribute('id')
        self.name=node.getAttribute('name')
        self.s=float(node.getAttribute('s'))
        self.t=float(node.getAttribute('t'))
        self.hdg=float(node.getAttribute('hdg'))
        self.type=node.getAttribute('type')
        outlines=node.getElementsByTagName('outline')
        if self.type=="crosswalk":
            self.outline=Outline(outlines[0],self)

class Objects:
    def __init__(self,node,map):
        self.objects=[]
        objects=node.getElementsByTagName('object')
        for object in objects:
            obj=Object(object)
            self.objects.append(obj)
            map.objects.append(obj)