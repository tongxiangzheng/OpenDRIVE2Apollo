from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs
import math
from numpy import pi,sqrt
import matplotlib.pyplot as plt
from pyclothoids import Clothoid

class Offset:
    def __init__(self,node):
        if node.hasAttribute('s'):
            self.s=float(node.getAttribute('s'))
        elif node.hasAttribute('sOffset'):
            self.s=float(node.getAttribute('sOffset'))
        else:
            log.error("offset parse error")
    
        self.a=float(node.getAttribute('a'))
        self.b=float(node.getAttribute('b'))
        self.c=float(node.getAttribute('c'))
        self.d=float(node.getAttribute('d'))

class Offsets:
    def __init__(self):
        self.offsets=[]
        self.s=0
    def addOffsets(self,nodeList):
        for node in nodeList:
             self.offsets.append(Offset(node))
        last=-1000000
        for offset in self.offsets:
            if last>offset.s:
                log.warning("offset order error")
            last=offset.s
    def setStart(self,s):
        self.s=s
    def getOffset(self,s,lim):
        s-=self.s
        # if lim=='+':
        #     s+=0.1
        # elif lim=='-':
        #     s-=0.1
        if len(self.offsets)==0:
            log.warning("len(self.offsets)==0")
            return 0
        p=0
        for i in range(len(self.offsets)):
            offset=self.offsets[i]
            if offset.s==s:
                if lim=='-':
                    break
            if offset.s>s:
                break
            p=i
        offset=self.offsets[p]
        s=s-offset.s
        # if lim=='+':
        #     s-=0.1
        # elif lim=='-':
        #     s+=0.1
        #return a+b*s+c*s^2+d*s^3
        return offset.a+s*(offset.b+s*(offset.c+s*offset.d))
    def print(self):
        print(self)
        print("len: ",len(self.offsets))
        for offset in self.offsets:
            print("s: "+str(offset.s+self.s)+" a: "+str(offset.a))

        
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
    def forward(self,length):
        self.x+=length*self.directX
        self.y+=length*self.directY

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
    def getDirect(self,s,laneLength):
        s-=self.s
        direct=Direct(self.x,self.y,self.hdg)
        limit=0.001
        nextL=limit
        if self.type=='line':
            #log.debug(str(direct.x)+" "+str(direct.y))
            #log.debug(str(direct.x)+" "+str(direct.y)+" "+str(direct.directX)+" "+str(direct.directY)+" "+str(s))
            direct.forward(s)
            #print(self.length/4)
            nextL=laneLength/3
        elif self.type=='arc':
            radius=1/self.curvature
            arc=s/radius
            #if self.curvature>0:
            direct.offset(radius)
            direct.setHdg(self.hdg+arc)
            direct.offset(-radius)
            #print(radius)
            nextL=abs(radius*0.05)
            nextL=min(nextL,laneLength/3)
        elif self.type=="spiral":
            direct.x=self.XList[int(s/self.len_per_point)]
            direct.y=self.YList[int(s/self.len_per_point)]
            arc=self.kd*s
            direct.setHdg(self.hdg+arc)
            nextL=self.len_per_point
        
        nextL=max(nextL,limit)
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
    def getLength(self):
        last=self.geometrys[-1]
        return last.s+last.length
    def parse(self,map):
        for geometry in self.geometrys:
            geometry.parse(map)