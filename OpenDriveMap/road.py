from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs
from collections import defaultdict

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
        self.ApolloPredecessors=[]
        self.ApolloSuccessors=[]
        self.left_neighbor_forward_lane=None
        self.left_neighbor_reverse_lane=None
        self.right_neighbor_reverse_lane=None
        self.right_neighbor_forward_lane=None
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
    
    def parse(self,curRoad,preRoads,sucRoads,leftLane,rightLane):
        self.ApolloName=curRoad.ApolloName+'_lane_'+self.id
        if self.predecessor is not None:
            for preRoad in preRoads:
                self.ApolloPredecessors.append(preRoad.findLaneByLaneLink(self.predecessor))
        if self.successor is not None:
            for sucRoad in sucRoads:
                self.ApolloSuccessors.append(sucRoad.findLaneByLaneLink(self.successor))
        if leftLane is not None:
            if int(self.id)*int(leftLane.id)<0:
                self.left_neighbor_reverse_lane=leftLane
            else:
                self.left_neighbor_forward_lane=leftLane
        if rightLane is not None:
            if int(self.id)*int(rightLane.id)<0:
                self.right_neighbor_reverse_lane=leftLane
            else:
                self.right_neighbor_forward_lane=leftLane
            

        
            
    def print(self):
        print("  "+self.ApolloName)
        if self.predecessor is not None:
            print("    predecessor:"+self.predecessor.ptr.ApolloName)
        if self.successor is not None:
            print("    successor:"+self.successor.ptr.ApolloName)
  
def defaultNoneLane():
    return None
class Lanes:
    def __init__(self,node):
        subDict=sub2dict(node)
        laneOffset=Offset(subDict['laneOffset'][0])

        subDict=sub2dict(subDict['laneSection'][0])
        
        self.lanes=defaultdict(defaultNoneLane)

        leftList=subDict['left']
        if len(leftList)==1:
            lanes=leftList[0].getElementsByTagName('lane')
            for lane in lanes:
                id=lane.getAttribute('id')
                self.lanes[id]=Lane(lane)
        else:
            log.error("lane:CE")

        rightList=subDict['right']
        if len(rightList)==1:
            lanes=rightList[0].getElementsByTagName('lane')
            for lane in lanes:
                id=lane.getAttribute('id')
                self.lanes[id]=Lane(lane)
        else:
            log.error("lane:CE")

    def getLaneById(self,id):
        return self.lanes[id]
    def parse(self,curRoad,preRoads,sucRoads):#当前road，当前road的前驱，当前road的后继
        for id,lane in self.lanes.items:
            i=int(id)
            leftLane=None
            rightLane=None
            if i>0:
                leftLane=self.getLaneById(str(i-1))
                rightLane=self.getLaneById(str(i+1))
                if(i==1):
                    leftLane=self.getLaneById("-1")
            else:
                leftLane=self.getLaneById(str(i+1))
                rightLane=self.getLaneById(str(i-1))
                if(i==1):
                    leftLane=self.getLaneById("1")

            lane.parse(curRoad,preRoads,sucRoads,leftLane,rightLane)
    def print(self):
        for lane in self.lanes:
            lane.print()
class Road:
    def __init__(self,node):
        self.name=node.getAttribute('name')
        self.length=node.getAttribute('length')
        self.id=node.getAttribute('id')
        self.junction=node.getAttribute('junction')
        self.predecessor=None
        self.successor=None
        self.ApolloPredecessor=[]
        self.ApolloSuccessor=[]
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
            link=self.predecessor
            if link.elementType=='road':
                self.ApolloPredecessor.append(map.findRoadById(link.elementId))
            elif link.elementType=='junction':
                junction=map.findJunctionById(link.elementId)
                self.ApolloPredecessor=junction.getIncomingRoad(self)
            else:
                log.warning("unknown link type")
        if self.successor is not None:
            link=self.successor
            if link.elementType=='road':
                self.ApolloSuccessor.append(map.findRoadById(link.elementId))
            elif link.elementType=='junction':
                junction=map.findJunctionById(link.elementId)
                self.ApolloSuccessor=junction.getConnectingRoad(self)
            else:
                log.warning("unknown link type")
        self.lanes.parse(self,self.ApolloPredecessor,self.ApolloSuccessor)
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

    