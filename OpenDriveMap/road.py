from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs


class RoadLink:
    def __init__(self,node):
        #print(node)
        self.kind=node.getElementsByTagName('name')
        self.elementType=node.getAttribute('elementType')
        self.ptr=None
        if self.elementType=='road':
            self.elementId=node.getAttribute('elementId')
            self.contactPoint=node.getAttribute('contactPoint')
        elif self.elementType=='junction':
            self.elementId=node.getAttribute('elementId')
        else:
            log.warning("unknown link type")
    def setPtr(self,ptr):
        self.ptr=ptr

class Speed:
    def __init__(self,node):
        self.max=node.getAttribute('max')
        self.unit=node.getAttribute('unit')
        
class Type:
    def __init__(self,node):
        self.type=node.getAttribute('type')
        self.speed=Speed(node.getElementsByTagName('speed')[0])
        
    
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


class PlanView:
    def __init__(self,node):
        self.geometrys=[]
        nodelist=node.getElementsByTagName('geometry')
        for node in nodelist:
            self.geometrys.append(Geometry(node))
    
class Offset:
    def __init__(self,node):
        self.s=node.getAttribute('s')
        self.a=node.getAttribute('a')
        self.b=node.getAttribute('b')
        self.c=node.getAttribute('c')
        self.d=node.getAttribute('d')

class LaneLink:
    def __init__(self,node):
        #print(node)
        self.id=node.getAttribute('id')
        self.ptr=None
    def setPtr(self,ptr):
        self.ptr=ptr

class Lane:
    def __init__(self,node):
        #dfs(node,1)
        self.id=node.getAttribute('id')
        subDict=sub2dict(node)
        linkList=subDict['link']
        if len(linkList)==1:
            links=linkList[0]
            if len(links.getElementsByTagName('predecessor'))==1:
                self.predecessor=LaneLink(links.getElementsByTagName('predecessor')[0])
            else:
                self.predecessor=None
            if len(links.getElementsByTagName('successor'))==1:
                self.successor=LaneLink(links.getElementsByTagName('successor')[0])
            else:
                self.successor=None
        else:
            self.predecessor=None
            self.successor=None
    
    def parse(self,curRoad,preRoad,sucRoad):
        self.ApolloName=curRoad.ApolloName+'_lane_'+self.id
        if self.predecessor is not None:
            self.predecessor.setPtr(preRoad.findLaneByLaneLink(self.predecessor))
        if self.successor is not None:
            self.successor.setPtr(sucRoad.findLaneByLaneLink(self.successor))
    def print(self):
        print("  "+self.ApolloName)
        if self.predecessor is not None:
            print("    predecessor:"+self.predecessor.ptr.ApolloName)
        if self.successor is not None:
            print("    successor:"+self.successor.ptr.ApolloName)
class Lanes:
    def __init__(self,node):
        subDict=sub2dict(node)
        laneOffset=Offset(subDict['laneOffset'][0])

        subDict=sub2dict(subDict['laneSection'][0])
        
        self.leftLanes=[]
        self.rightLanes=[]

        leftList=subDict['left']
        if len(leftList)==1:
            lanes=leftList[0].getElementsByTagName('lane')
            for lane in lanes:
                self.leftLanes.append(Lane(lane))


        rightList=subDict['right']
        if len(rightList)==1:
            lanes=rightList[0].getElementsByTagName('lane')
            for lane in lanes:
                self.rightLanes.append(Lane(lane))

    def getLaneById(self,id):
        for lane in self.leftLanes:
            if lane.id==id:
                return lane
        for lane in self.rightLanes:
            if lane.id==id:
                return lane
        return None
    def parse(self,curRoad,preRoad,sucRoad):#当前road，当前road的前驱，当前road的后继
        for lane in self.leftLanes:
            lane.parse(curRoad,preRoad,sucRoad)
        for lane in self.rightLanes:
            lane.parse(curRoad,preRoad,sucRoad)
    def print(self):
        for lane in self.leftLanes:
            lane.print()
        for lane in self.rightLanes:
            lane.print()
class Road:
    def __init__(self,node):
        self.name=node.getAttribute('name')
        self.length=node.getAttribute('length')
        self.id=node.getAttribute('id')
        self.junction=node.getAttribute('junction')
        #self.rule="RHT" 默认靠右行驶

        subDict=sub2dict(node)
        #log.debug("road id: "+self.id)

        #link
        linkList=subDict['link']
        for links in linkList:
            if len(links.getElementsByTagName('predecessor'))>2:
                log.warning("road:predecessor too much")
            if len(links.getElementsByTagName('successor'))>2:
                log.warning("road:successor too much")
            
            for l in links.getElementsByTagName('predecessor'):
                self.predecessor=RoadLink(l)
            for l in links.getElementsByTagName('successor'):
                self.successor=RoadLink(l)
        
        #type
        typeList=subDict['type']
        if len(typeList) == 1:
            self.type=Type(typeList[0])
        #else:
            #log.info("road id "+self.id+" : have no type or too much types")

        #planView
        planViewList=subDict['planView']
        self.planView=PlanView(planViewList[0])

        #lane
        laneList=subDict['lanes']
        self.lanes=Lanes(laneList[0])
    

    def findLaneByLaneLink(self,link):
        #<debug>
        if self.lanes.getLaneById(link.id) is None:
            log.Info("lane:"+self.ApolloName+"cannot find lane id:"+id)
        #</debug>
        return self.lanes.getLaneById(link.id)
    
    def parse(self,map):
        self.ApolloName='road_'+self.id
        if self.predecessor is not None:
            self.predecessor.setPtr(map.findRoadByRoadLink(self.predecessor))
        if self.successor is not None:
            self.successor.setPtr(map.findRoadByRoadLink(self.successor))
        self.lanes.parse(self,self.predecessor.ptr,self.successor.ptr)
    def print(self):
        print(self.ApolloName)
        self.lanes.print()

class Roads:
    def __init__(self,nodeList):
        self.roads=dict()
        for node in nodeList:
            id=node.getAttribute('id')
            #print(id)
            self.roads[id]=Road(node)

    def parse(self,map):
        for id,road in self.roads.items():
            road.parse(map)
    def print(self):
        for id,road in self.roads.items():
            road.print()

    