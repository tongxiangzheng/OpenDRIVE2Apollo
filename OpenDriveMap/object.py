from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,Counter
from OpenDriveMap.planView import Direct

class Overlap_crosswalk_lane:
    def __init__(self,crosswalk,lane):
        self.kind="crosswalk_with_lane"
        crosswalk.overlap_crosswalk_lanes.append(self)
        lane.overlap_crosswalk_lanes.append(self)
        self.crosswalk=crosswalk
        self.lane=lane
    def getApolloName(self):
        ApolloName='overlap_CW_'+self.crosswalk.ApolloId+'_lane_'+self.lane.ApolloId
        return ApolloName
    
class CornerLocal:
    def __init__(self,node):
        self.u=float(node.getAttribute('u'))
        self.v=float(node.getAttribute('v'))
        self.z=float(node.getAttribute('z'))
    def getDirect(self,referenceDirect):
        direct=referenceDirect.copy()
        direct.offset(self.v)
        direct.forward(self.u)
        return direct
    
class Outline:
    def __init__(self,node,object):
        self.object=object
        self.cornerLocals=[]
        cornerLocals=node.getElementsByTagName('cornerLocal')
        for cornerLocal in cornerLocals:
            self.cornerLocals.append(CornerLocal(cornerLocal))
            
class Object:
    def __init__(self,node,road):
        self.road=road
        self.id=node.getAttribute('id')
        self.name=node.getAttribute('name')
        self.s=float(node.getAttribute('s'))
        self.t=float(node.getAttribute('t'))
        self.hdg=float(node.getAttribute('hdg'))
        self.type=node.getAttribute('type')
        outlines=node.getElementsByTagName('outline')
        self.overlap_crosswalk_lanes=[]
        if self.type=="crosswalk":
            self.outline=Outline(outlines[0],self)
    def parse(self,map):
        self.ApolloId=self.id
        self.ApolloName="CW_"+self.ApolloId
    def setPolygon(self,polygon):
        self.polygon=polygon
    def parse_junction(self,map):
        junction=self.road.junction
        for overlap in junction.overlap_junction_lanes:
            lane=overlap.lane
            if lane.type!="driving":
                continue
            if self.checkIntersect(lane.centralCurve) == True:
                map.addOverlap(Overlap_crosswalk_lane(self,lane))

    def checkIntersect(self,centralCurve):
        polygon=self.polygon
        for lineC in centralCurve.lines:
            for lineP in polygon.lines:
                if lineC.intersect(lineP):
                    return True
        return False

class Objects:
    def __init__(self,node,road,map):
        self.objects=[]
        objects=node.getElementsByTagName('object')
        for object in objects:
            obj=Object(object,road)
            self.objects.append(obj)
            map.objects.append(obj)
    def parse(self,map):
        for object in self.objects:
            object.parse(map)