from math import sqrt
from OpenDriveMap.road import Offsets
class OffsetsDict:
    def __init__(self):
        self.offsetsList=[]
    def addOffsets(self,offsets,coefficient):
        self.offsetsList.append((offsets,coefficient))
    def popOffsets(self):
        self.offsetsList.pop()
    def getOffset(self,s):
        ans=0
        return 0
        for offsets,coefficient in self.offsetsList:
            ans=ans+offsets.getOffset(s)*coefficient
        return ans
class Point:
    def __init__(self,s,x,y,transformer):
        self.s=float(s)
        self.x=float(x)
        self.y=float(y)
        self.x,self.y=transformer.transform(self.x,self.y)
        self.preLine=None
        self.sucLine=None
class Line:
    def __init__(self,prePoint,sucPoint):
        self.prePoint=prePoint
        prePoint.sucLine=self
        self.sucPoint=sucPoint
        sucPoint.preLine=self
        self.calcLength()
    def calcLength(self):
        self.length=sqrt((self.prePoint.x-self.sucPoint.x)**2+(self.prePoint.y-self.sucPoint.y)**2)
class LanePoint:
    def __init__(self,Curve,offset):
        "continue"
class Curve:
    def __init__(self,PlanView,offsetsDict,transformer):
        #-------------------
        SIM_SPEED=10
        #-------------------

        self.points=[]
        self.lines=[]
        p=0
        s=0

        while p<len(PlanView.geometrys):
            geometry=PlanView.geometrys[p]
            if s>geometry.length+geometry.s:
                s=geometry.length+geometry.s
                p+=1
            direct=geometry.getDirect(geometry.length+geometry.s)
            s+=SIM_SPEED
            direct.offset(offsetsDict.getOffset(s))
            self.addPoint(Point(s,direct.x,direct.y,transformer))
        #for geometry in PlanView.geometrys:
            #self.addPoint(Point(geometry.s,geometry.x,geometry.y,transformer))
        
    def addPoint(self,point):
        self.points.append(point)
        if len(self.points)>=2:
            self.lines.append(Line(self.points[-2],self.points[-1]))
    def getLength(self):
        len=0.0
        for line in self.lines:
            len+=line.length
        return len