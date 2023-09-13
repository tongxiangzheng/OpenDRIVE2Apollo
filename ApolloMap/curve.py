from loguru import logger as log
from math import sqrt
from OpenDriveMap.road import Offsets
from OpenDriveMap.object import Object
from OpenDriveMap.planView import limit

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
    def copy(self):
        offsetsDict=OffsetsDict()
        for offsets,coefficient in self.offsetsList:
            offsetsDict.addOffsets(offsets,coefficient)
        return offsetsDict
class Point:
    def __init__(self,x,y,transformer):
        self.x=x
        self.y=y
        
        self.x+=586251
        self.y+=4141282
        
        #self.x,self.y=transformer.transform(self.x,self.y)

        self.preLine=None
        self.sucLine=None
    def reverse(self):
        self.preLine,self.sucLine=self.sucLine,self.preLine

class Vector:
    def __init__(self,prePoint,sucPoint):
        self.x=sucPoint.x-prePoint.x
        self.y=sucPoint.y-prePoint.y
    def mul(self,vectorA):
        #print(self.x*vectorA.y-self.y*vectorA.x)
        return self.x*vectorA.y-self.y*vectorA.x
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
    def intersect(self,lineA):
        if self.cross(lineA) == True and lineA.cross(self) == True:
            return True
        return False
    def cross(self,lineA):
        selfV=Vector(self.prePoint,self.sucPoint)
        Aa=Vector(self.prePoint,lineA.prePoint)
        Ab=Vector(self.prePoint,lineA.sucPoint)
        if Aa.mul(selfV)*Ab.mul(selfV)<0:
            return True
        return False


class RoadPoint:
    def __init__(self,PlanView,s,t,transformer):
        p=0
        while p<len(PlanView.geometrys):
            geometry=PlanView.geometrys[p]
            if s<=geometry.s+geometry.length+limit:
                break
            else:
                p+=1
        if p==len(PlanView.geometrys):
            p-=1
            log.info("s: "+str(s)+" is larger than planview length: "+str(geometry.s+geometry.length))
        geometry=PlanView.geometrys[p]
        direct,nextL=geometry.getDirect(s,0)
        direct.offset(t)
        self.direct=direct
        self.transformer=transformer
        self.point=Point(direct.x,direct.y,transformer)
    def Offset(self,s):
        self.direct.offset(s)
        self.point=Point(self.direct.x,self.direct.y,self.transformer)


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
        debugLaneName='lane_-1_1_1'
        if lane.ApolloName==debugLaneName:
            print("---------")
            print("lane: ",lane.s,lane.t)
            print("len(PlanView.geometrys): ",len(PlanView.geometrys))
        
        lastS=0.0
        while p<len(PlanView.geometrys):
            geometry=PlanView.geometrys[p]
            if lane.ApolloName==debugLaneName:
                print("s,p,t: ",s,p,lane.t)
                print("planView: ",PlanView.geometrys[p].s,PlanView.geometrys[p].length)
            if s+limit>=geometry.length+geometry.s:
                p+=1
                if p==len(PlanView.geometrys):
                    break
                s=max(PlanView.geometrys[p].s,lastS+limit)
                #direct,nextL=geometry.getDirect(s)
                #direct.offset(offsetsDict.getOffset(s,'-'))
                #self.addPoint(Point(s,direct.x,direct.y,transformer))
                continue
            if s+limit>=lane.t:
                break
            #log.info(str(s)+" "+str(geometry.length+geometry.s))
            if lane.ApolloName==debugLaneName:
                print("getDirect: s is ",s)
            direct,nextL=geometry.getDirect(s,lane.length)
            if lane.ApolloName==debugLaneName:
                print("end getDirect ",s)
            direct.offset(offsetsDict.getOffset(s,'+'))
            if lane.ApolloName==debugLaneName:
                print("s: ",s)
                print("offsets: ",offsetsDict.getOffset(s,'+'))
            lastS=s
            s+=nextL
            self.addPoint(Point(direct.x,direct.y,transformer))
            if notes=="central" and len(self.points)>=2 and self.lines[-1].length<limit*0.5:
                line=self.lines[-1]
                log.warning("two point is too near at ("+str(line.prePoint.x)+","+str(line.prePoint.y)+") and ("+str(line.sucPoint.x)+","+str(line.sucPoint.y)+")")
                log.warning("it's happend at middle of "+lane.ApolloName)
                log.warning("at "+str(p)+"th geometry,it's type is "+geometry.type)
                log.warning("s: "+str(s)+" geometry.s: "+str(geometry.s)+" geometry.length: "+str(geometry.s))
        if p==len(PlanView.geometrys):
            p-=1
        
        geometry=PlanView.geometrys[p]
        s=lane.t
        while s<geometry.s:
            p-=1
            geometry=PlanView.geometrys[p]

        direct,nextL=geometry.getDirect(s,lane.length)
        direct.offset(offsetsDict.getOffset(s,'-'))
        self.addPoint(Point(direct.x,direct.y,transformer))
        if len(self.points)>=2 and self.lines[-1].length<limit*0.5:
            line=self.lines[-1]
            log.warning("two point is too near at ("+str(line.prePoint.x)+","+str(line.prePoint.y)+") and ("+str(line.sucPoint.x)+","+str(line.sucPoint.y)+")")
            log.warning("it's happend at end of"+lane.ApolloName)

        if len(self.points)<=3:
            log.warning(lane.fullName+": too less point : len="+str(len(self.points)))
            log.warning("length of lane is "+str(lane.length))
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

class Polygon:
    def __init__(self,object,transformer):
        self.points=[]
        self.lines=[]
        outline=object.outline
        s=object.s
        t=object.t
        hdg=object.hdg
        #referencePoint=RoadPoint(object.road.planView,s,t,transformer)
        referencePoint=RoadPoint(object.road.planView,s,t,transformer)
        referenceDirect=referencePoint.direct
        
        referenceDirect.setHdg(referencePoint.direct.hdg+hdg)

        # direct=referenceDirect.copy()
        # direct.offset(-5)
        # direct.forward(-1)
        # self.addPoint(Point(direct.x,direct.y,transformer))
        
        # direct=referenceDirect.copy()
        # direct.offset(-5)
        # direct.forward(1)
        # self.addPoint(Point(direct.x,direct.y,transformer))

        # direct=referenceDirect.copy()
        # direct.offset(5)
        # direct.forward(1)
        # self.addPoint(Point(direct.x,direct.y,transformer))

        # direct=referenceDirect.copy()
        # direct.offset(5)
        # direct.forward(-1)
        # self.addPoint(Point(direct.x,direct.y,transformer))

        # self.addPoint(referencePoint.point)

        for cornerLocal in outline.cornerLocals:
            if cornerLocal==outline.cornerLocals[-1]:
                break
            direct=cornerLocal.getDirect(referenceDirect)
            self.addPoint(Point(direct.x,direct.y,transformer))
            
    def addPoint(self,point):
        self.points.append(point)
        if len(self.points)>=2:
            self.lines.append(Line(self.points[-2],self.points[-1]))

        