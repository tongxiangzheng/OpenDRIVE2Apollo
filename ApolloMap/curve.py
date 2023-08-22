from loguru import logger as log
from math import sqrt
from OpenDriveMap.road import Offsets
class OffsetsDict:
    def __init__(self):
        self.offsetsList=[]
    def addOffsets(self,offsets,coefficient):
        self.offsetsList.append((offsets,coefficient))
    def popOffsets(self):
        self.offsetsList.pop()
    def getOffset(self,s,lim):
        ans=0
        for offsets,coefficient in self.offsetsList:
            ans=ans+offsets.getOffset(s,lim)*coefficient
        return ans
class Point:
    def __init__(self,s,x,y,transformer):
        self.s=float(s)
        self.x=float(x)
        self.y=float(y)

        self.x,self.y=transformer.transform(self.x,self.y)

        self.preLine=None
        self.sucLine=None
    def reverse(self):
        self.preLine,self.sucLine=self.sucLine,self.preLine
        
class Line:
    def __init__(self,prePoint,sucPoint):
        self.prePoint=prePoint
        prePoint.sucLine=self
        self.sucPoint=sucPoint
        sucPoint.preLine=self
        self.calcLength()
    def calcLength(self):
        self.length=sqrt((self.prePoint.x-self.sucPoint.x)**2+(self.prePoint.y-self.sucPoint.y)**2)
    def reverse(self):
        self.prePoint,self.sucPoint=self.sucPoint,self.prePoint
        
class Curve:
    def __init__(self,PlanView,offsetsDict,lane,transformer):
        self.points=[]
        self.lines=[]
        s=lane.s
        p=0
        while p<len(PlanView.geometrys):
            geometry=PlanView.geometrys[p]
            if s<=geometry.s+geometry.length:
                break
            else:
                p+=1
        debugLaneName='none'
        if lane.fullName==debugLaneName:
            print("---------")
            print("lane: ",lane.s,lane.t)
            print("len(PlanView.geometrys): ",len(PlanView.geometrys))
        while p<len(PlanView.geometrys):
            geometry=PlanView.geometrys[p]
            if lane.fullName==debugLaneName:
                print("s,p,t: ",s,p,lane.t)
                print("planView: ",PlanView.geometrys[p].s,PlanView.geometrys[p].length)
            if s>geometry.length+geometry.s:
                s=geometry.length+geometry.s
                p+=1
                continue
            if s>=lane.t:
                break
            #log.info(str(s)+" "+str(geometry.length+geometry.s))
            direct,nextL=geometry.getDirect(s)
            direct.offset(offsetsDict.getOffset(s,'+'))
            if lane.fullName==debugLaneName:
                offsetsDict.offsetsList[0][0].print()
                print("s: ",s)
                print("offsets: ",offsetsDict.offsetsList[0][0].getOffset(s,'+'))
                print("offsets: ",offsetsDict.getOffset(s,'+'))
            s+=nextL
            self.addPoint(Point(s,direct.x,direct.y,transformer))
        if p==len(PlanView.geometrys):
            p-=1

        geometry=PlanView.geometrys[p]
        s=lane.t
        # if lane.fullName=='lane_782_0_-1':
        #     print("s,p,t: ",s,p,lane.t)
        #     print("planView: ",PlanView.geometrys[p].s,PlanView.geometrys[p].length)
        direct,nextL=geometry.getDirect(s)
        direct.offset(offsetsDict.getOffset(s,'-'))
        #if lane.fullName=='lane_782_0_-3':
        #    print("direct: ",direct.x,direct.y)
        self.addPoint(Point(s,direct.x,direct.y,transformer))
        #for geometry in PlanView.geometrys:
            #self.addPoint(Point(geometry.s,geometry.x,geometry.y,transformer))
        #log.info("----------------------------------")
        if lane.forward==-1:
            self.reverse()
    def addPoint(self,point):
        self.points.append(point)
        if len(self.points)>=2:
            self.lines.append(Line(self.points[-2],self.points[-1]))
    def getLength(self):
        len=0.0
        for line in self.lines:
            len+=line.length
        return len
    def reverse(self):
        for point in self.points:
            point.reverse()
        for line in self.lines:
            line.reverse()
        self.points.reverse()
        self.lines.reverse()
