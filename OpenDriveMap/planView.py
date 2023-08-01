from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs
import math
class Direct:
    def __init__(self,x,y,hdg):
        self.x=x
        self.y=y
        self.directX=math.sin(hdg)
        self.directY=math.sin(hdg)
    def run(self,s):
        self.x+=self.directX*s
        self.y+=self.directY*s
        
class Geometry:
    def __init__(self,node):
        #dfs(node,1)
        self.s=node.getAttribute('s')
        self.x=node.getAttribute('x')
        self.y=node.getAttribute('y')
        self.hdg=node.getAttribute('hdg')
        self.length=node.getAttribute('length')
        self.type="unknown"
        if len(node.getElementsByTagName('line'))==1:
            self.type="line"
        elif len(node.getElementsByTagName('spiral'))==1:
            self.type="spiral"
            log.warning("Geometry:not support spiral")
            #暂不支持螺旋线
        elif len(node.getElementsByTagName('arc'))==1:
            self.type="arc"
            self.curvature=node.getElementsByTagName('arc')[0].getAttribute('curvature')
            #log.debug("Geometry:arc curvature is "+self.curvature)

        else:
            log.warning("Geometry:unknown geometry type")
    def getDirect(self,s):
        if self.type=="line":
            direct=Vector(self.x,self.y,self.hdg)
            direct.run(s)
            return direct
    def parse(self,map):
        "nothting"
        

class PlanView:
    def __init__(self,node):
        self.geometrys=[]
        nodelist=node.getElementsByTagName('geometry')
        for node in nodelist:
            self.geometrys.append(Geometry(node))
    def parse(self,map):
        for geometry in self.geometrys:
            geometry.parse(map)