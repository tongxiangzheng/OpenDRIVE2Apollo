from loguru import logger as log
from math import sqrt
from OpenDriveMap.road import Offsets
from OpenDriveMap.object import Object

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
        
class RoadPoint:
    def __init__(self,PlanView,s,t,transformer):
        p=0
        while p<len(PlanView.geometrys):
            geometry=PlanView.geometrys[p]
            if s<=geometry.s+geometry.length:
                break
            else:
                p+=1
        direct,nextL=geometry.getDirect(s,0)
        direct.offset(t)
        s+=nextL
        self.direct=direct
        self.transformer=transformer
        self.point=Point(s,direct.x,direct.y,transformer)
    def Offset(self,s):
        self.direct.offset(s)
        self.point=Point(s,self.direct.x,self.direct.y,self.transformer)


class Curve:
    def __init__(self,PlanView,offsetsDict,lane,transformer,notes):
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
        if lane.ApolloName==debugLaneName:
            print("---------")
            print("lane: ",lane.s,lane.t)
            print("len(PlanView.geometrys): ",len(PlanView.geometrys))
        
        limit=0.0001
        lastS=0.0
        while p<len(PlanView.geometrys):
            geometry=PlanView.geometrys[p]
            if lane.ApolloName==debugLaneName:
                print("s,p,t: ",s,p,lane.t)
                print("planView: ",PlanView.geometrys[p].s,PlanView.geometrys[p].length)
            if s+limit>=geometry.length+geometry.s:
                s=max(geometry.length+geometry.s,lastS+limit)
                #direct,nextL=geometry.getDirect(s)
                #direct.offset(offsetsDict.getOffset(s,'-'))
                #self.addPoint(Point(s,direct.x,direct.y,transformer))
                p+=1
                continue
            if s+limit>=lane.t:
                break
            #log.info(str(s)+" "+str(geometry.length+geometry.s))
            direct,nextL=geometry.getDirect(s,lane.length)
            direct.offset(offsetsDict.getOffset(s,'+'))
            if lane.ApolloName==debugLaneName:
                print("s: ",s)
                print("offsets: ",offsetsDict.getOffset(s,'+'))
            lastS=s
            s+=nextL
            self.addPoint(Point(s,direct.x,direct.y,transformer))
            if notes=="central" and len(self.points)>=2 and self.lines[-1].length<limit*0.5:
                line=self.lines[-1]
                log.warning("two point is too near at ("+str(line.prePoint.x)+","+str(line.prePoint.y)+") and ("+str(line.sucPoint.x)+","+str(line.sucPoint.y)+")")
                log.warning("it's happend at middle of "+lane.ApolloName)
                log.warning("at "+str(p)+"th geometry,it's type is "+geometry.type)
                log.warning("s: "+str(s)+" geometry.s: "+str(geometry.s)+" geometry.length: "+str(geometry.s))
        if p==len(PlanView.geometrys):
            p-=1
        if True is True:
            geometry=PlanView.geometrys[p]
            s=lane.t
            direct,nextL=geometry.getDirect(s,lane.length)
            direct.offset(offsetsDict.getOffset(s,'-'))
            self.addPoint(Point(s,direct.x,direct.y,transformer))
            if len(self.points)>=2 and self.lines[-1].length<limit*0.5:
                line=self.lines[-1]
                log.warning("two point is too near at ("+str(line.prePoint.x)+","+str(line.prePoint.y)+") and ("+str(line.sucPoint.x)+","+str(line.sucPoint.y)+")")
                log.warning("it's happend at end of"+lane.ApolloName)
    
        else:
            log.info("skip a point at end of lane")
        if len(self.points)<=3:
            log.warning(lane.ApolloName+": too less point : len="+str(len(self.points)))
            log.warning("length of lane is "+str(lane.length))
        if lane.forward==1:
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

class polygon:
    def __init__(self,object):
        self.points=[]
        outline=object.outline
        s=object.s
        t=object.t
        hdg=object.hdg
        for cornerLocal in outline.cornerLocals:
            "continue"
    
    def addPoint(self,point):
        self.points.append(point)
        