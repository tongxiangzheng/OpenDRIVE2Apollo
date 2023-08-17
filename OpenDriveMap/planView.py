from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs
import math
from numpy import pi,sqrt
import matplotlib.pyplot as plt
from pyclothoids import Clothoid

class Direct:
    def __init__(self,x,y,hdg):
        self.x=x
        self.y=y
        self.directX=math.cos(hdg)
        self.directY=math.sin(hdg)
    def offset(self,offset):
        offsetDirectX=-self.directY
        offsetDirectY=self.directX
        self.x+=offset*offsetDirectX
        self.y+=offset*offsetDirectY
    def setHdg(self,hdg):
        self.directX=math.cos(hdg)
        self.directY=math.sin(hdg)

        
class Geometry:
    def __init__(self,node):
        #dfs(node,1)
        self.s=float(node.getAttribute('s'))
        self.x=float(node.getAttribute('x'))
        self.y=float(node.getAttribute('y'))

        #log.debug(node.getAttribute('x')+' '+node.getAttribute('y')+' '+str(self.x)+" "+str(self.y))

        self.hdg=float(node.getAttribute('hdg'))
        self.length=float(node.getAttribute('length'))
        self.type="unknown"
        if len(node.getElementsByTagName('line'))==1:
            self.type="line"
        elif len(node.getElementsByTagName('spiral'))==1:
            self.type="spiral"
            self.curvStart=float(node.getElementsByTagName('spiral')[0].getAttribute('curvStart'))
            self.curvEnd=float(node.getElementsByTagName('spiral')[0].getAttribute('curvEnd'))
        elif len(node.getElementsByTagName('arc'))==1:
            self.type="arc"
            self.curvature=float(node.getElementsByTagName('arc')[0].getAttribute('curvature'))
            #log.debug("Geometry:arc curvature is "+self.curvature)

        else:
            log.warning("Geometry:unknown geometry type")
    def getDirect(self,s,forward):
        s-=self.s
        direct=Direct(self.x,self.y,self.hdg)
        nextL=10.0
        if self.type=='line':
            #log.debug(str(direct.x)+" "+str(direct.y))
            #log.debug(str(direct.x)+" "+str(direct.y)+" "+str(direct.directX)+" "+str(direct.directY)+" "+str(s))
            direct.x+=direct.directX*s
            direct.y+=direct.directY*s
            nextL=10.0
        elif self.type=='arc':
            radius=1/self.curvature
            arc=s/radius
            #if self.curvature>0:
            direct.offset(radius)
            direct.setHdg(self.hdg+arc)
            direct.offset(-radius)
            #print(radius)
            nextL=abs(radius*0.02)
        elif self.type=="spiral":
            direct.x=self.XList[int(s/self.len_per_point)]
            direct.y=self.YList[int(s/self.len_per_point)]
            arc=self.kd*s
            direct.setHdg(self.hdg+arc)
            nextL=self.len_per_point

        return direct,nextL
    def parse(self,map):
        if self.type=="spiral":
            self.kd=(self.curvEnd-self.curvStart)/self.length
            clothoid = Clothoid.StandardParams(self.x, self.y, self.hdg, self.curvStart,self.kd, self.length)
            directList=clothoid.SampleXY(int(self.length)+1)
            self.len_per_point=self.length/int(self.length)
            self.XList=directList[0]
            self.YList=directList[1]
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