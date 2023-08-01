from math import sqrt
from OpenDriveMap.road import Offsets
class OffsetsDict:
    def __init__(self):
        self.offsetsList=[]
    def addOffsets(self,offsets):
        self.offsetsList.append(offsets)
    def getOffset(self,s):
        ans=0
        for offsets in self.offsetsList:
            ans=ans+offsets.getOffset(s)
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
        self.points=[]
        self.lines=[]
        for geometry in PlanView.geometrys:
            self.addPoint(Point(geometry.s,geometry.x,geometry.y,transformer))
        "continue"
    def addPoint(self,point):
        self.points.append(point)
        if len(self.points)>=2:
            self.lines.append(Line(self.points[-2],self.points[-1]))
    def getLength(self):
        len=0.0
        for line in self.lines:
            len+=line.length
        return len