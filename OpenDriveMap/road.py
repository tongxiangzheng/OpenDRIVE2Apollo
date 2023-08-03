from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,Counter

from OpenDriveMap.planView import PlanView

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
    def __init__(self,nodeList):
        self.offsets=[]
        for node in nodeList:
             self.offsets.append(Offset(node))
    def getOffset(self,s):
        p=0
        for i in range(len(self.offsets)):
            offset=self.offsets[i]
            if offset.s>s:
                break
            p=i
        offset=self.offsets[p]
        s=s-offset.s
        #return a+b*s+c*s^2+d*s^3
        return offset.a+s*(offset.b+s*(offset.c+s*offset.d))
        
class LaneLink:
    def __init__(self,node):
        #print(node)
        self.id=node.getAttribute('id')
        self.ptr=None
    def setPtr(self,ptr):
        self.ptr=ptr

class Overlap_junction_lane:
    def __init__(self,junction,lane):
        self.kind="junction_with_lane"
        junction.overlap_junction_lanes.append(self)
        lane.overlap_junction_lane=self
        self.junction=junction
        self.lane=lane
        self.ApolloName='overlap_junction_I0_J'+junction.ApolloId+'_'+lane.ApolloName

class Lane:
    def __init__(self,node):
        #dfs(node,1)
        self.id=node.getAttribute('id')
        self.type=node.getAttribute('type')
        subDict=sub2dict(node)
        linkList=subDict['link']
        self.ApolloPredecessors=[]
        self.ApolloSuccessors=[]
        self.left_neighbor_forward_lane=None
        self.left_neighbor_reverse_lane=None
        self.right_neighbor_reverse_lane=None
        self.right_neighbor_forward_lane=None
        self.junction=None
        self.overlap_junction_lane=None
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
        #offsetList=subDict['roadMark']
        self.widthOffsets=Offsets(subDict['width'])

    def addConnect(self,lane,contactPoint):
        if contactPoint=='start':
            if int(self.id)<0:
                self.addPredecessor(lane)
            else:
                self.addSuccessor(lane)
        elif contactPoint=='end':
            if int(self.id)<0:
                self.addSuccessor(lane)
            else:
                self.addPredecessor(lane)
        else:
            log.error("unknown contackPoint: "+contactPoint)
    def addPredecessor(self,predecessor):
        if predecessor not in self.ApolloPredecessors:
            self.ApolloPredecessors.append(predecessor)
    def addSuccessor(self,successor):
        if successor not in self.ApolloSuccessors:
            self.ApolloSuccessors.append(successor)

    def parse(self,curRoad,preLink,sucLink,leftLane,rightLane,map,laneCounter):
        self.ApolloId=laneCounter.getId()
        self.ApolloName='lane_'+self.ApolloId
        # self.ApolloName='lane_'+curRoad.id+"00"+self.id
        # self.ApolloName=self.ApolloName.replace("-", "9")
        if int(self.id)>0:
            self.forward=-1
            preLink,sucLink=sucLink,preLink     #swap
            #leftLane,rightLane=rightLane,leftLane
            self.predecessor,self.successor=self.successor,self.predecessor
        else:
            self.forward=1

        self.junction=curRoad.junction
        if self.junction is not None:
            map.addOverlap(Overlap_junction_lane(self.junction,self))
        self.road=curRoad
        
        if self.predecessor is not None:
            if preLink.elementType!='road':
                log.error("parse: lane id:"+self.ApolloName+" should have one road as pre")
            preRoad=preLink.ptr
            predecessor=preRoad.getLaneByLaneLink(self.predecessor)
            self.addPredecessor(predecessor)
            if self.junction is not None:
                #log.debug(predecessor.ApolloName+" add (maybe)suc lane:"+self.ApolloName+" as "+preLink.contactPoint)
                predecessor.addConnect(self,preLink.contactPoint)
        else:
            if preLink.elementType!='junction':
                log.error("parse: lane id:"+self.ApolloName+" should have one junction as pre")
            preJunction=preLink.ptr
            predecessors=preJunction.getIncomingLane(curRoad,self)
            for predecessor in predecessors:
                self.addPredecessor(predecessor)

        if self.successor is not None:
            if sucLink.elementType!='road':
                log.error("parse: lane id:"+self.ApolloName+" should have one road as suc")
            sucRoad=sucLink.ptr
            successor=sucRoad.getLaneByLaneLink(self.successor)
            self.addSuccessor(successor)
            if self.junction is not None:
                #log.debug(successor.ApolloName+"add (maybe)pre lane:"+self.ApolloName)
                successor.addConnect(self,sucLink.contactPoint)
        else:
            if sucLink.elementType!='junction':
                log.error("parse: lane id:"+self.ApolloName+" should have one junction as suc")
            sucJunction=sucLink.ptr
            successors=sucJunction.getConnectingLane(curRoad,self)
            for successor in successors:
                self.addSuccessor(successor)
        # if self.successor is not None:
        #     if len(sucRoads)!=1:
        #         log.error("parse: lane id:"+self.ApolloName+" should have one road as suc")
        #     for sucRoad in sucRoads:
        #         self.ApolloSuccessors.append(sucRoad.findLaneByLaneLink(self.successor))
                
        if leftLane is not None:
            if int(self.id)*int(leftLane.id)<0:
                self.left_neighbor_reverse_lane=leftLane
            else:
                self.left_neighbor_forward_lane=leftLane
        if rightLane is not None:
            if int(self.id)*int(rightLane.id)<0:
                self.right_neighbor_reverse_lane=rightLane
            else:
                self.right_neighbor_forward_lane=rightLane
            

        
            
    def print(self):
        print("  "+self.ApolloName)
        if self.predecessor is not None:
            print("    predecessor:"+self.predecessor.ptr.ApolloName)
        if self.successor is not None:
            print("    successor:"+self.successor.ptr.ApolloName)
  
class Lanes:
    def __init__(self,node):
        subDict=sub2dict(node)
        self.laneOffsets=Offsets(subDict['laneOffset'])

        subDict=sub2dict(subDict['laneSection'][0])
        
        self.lanes=dict()

        leftList=subDict['left']
        if len(leftList)==1:
            lanes=leftList[0].getElementsByTagName('lane')
            for lane in lanes:
                id=lane.getAttribute('id')
                self.lanes[id]=Lane(lane)
        elif len(leftList)>1:
            log.error("lane:leftList size error: len=",len(leftList))

        # centerList=subDict['center']
        # if len(centerList)==1:
        #     lanes=centerList[0].getElementsByTagName('lane')
        #     for lane in lanes:
        #         id=lane.getAttribute('id')
        #         self.lanes[id]=Lane(lane)
        # elif len(centerList)>1:
        #     log.error("lane:centerList size error: len=",len(leftList))

        rightList=subDict['right']
        if len(rightList)==1:
            lanes=rightList[0].getElementsByTagName('lane')
            for lane in lanes:
                id=lane.getAttribute('id')
                self.lanes[id]=Lane(lane)
        elif len(rightList)>1:
            log.error("lane:rightList size error: len=",len(rightList))

    def getLaneById(self,id):
        if id in self.lanes:
            return self.lanes[id]
        if id!='.':
            log.error("cannot find id:"+id)
        return None
    def parse(self,curRoad,preLink,sucLink,map,laneCounter):#当前road，当前road的前驱，当前road的后继
        lis=list(self.lanes)
        lis.append(".")
        for i in range(len(lis)):
            id=lis[i]
            if id=='.':
                break
            lane=self.getLaneById(id)
            leftLane=None
            rightLane=None
            if int(id)>0:
                leftLane=self.getLaneById(lis[i+1]) #列表中id倒序，左侧车道id较小，所以在列表中较大下标位置
                rightLane=self.getLaneById(lis[i-1])
            else:
                leftLane=self.getLaneById(lis[i-1])
                rightLane=self.getLaneById(lis[i+1])
            lane.parse(curRoad,preLink,sucLink,leftLane,rightLane,map,laneCounter)
    def print(self):
        for lane in self.lanes:
            lane.print()
class Road:
    def __init__(self,node):
        self.name=node.getAttribute('name')
        self.length=node.getAttribute('length')
        self.id=node.getAttribute('id')
        self.junction=node.getAttribute('junction')
        if self.junction=='-1':
            self.junction=None
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
    

    def getLaneByLaneLink(self,laneLink):
        #<debug>
        #if self.lanes.getLaneById(link.id) is None:
        #    log.Info("lane:"+self.ApolloName+"cannot find lane id:"+id)
        #</debug>
        return self.lanes.getLaneById(laneLink.id)
    
    def getLaneById(self,id):
        #<debug>
        #if self.lanes.getLaneById(link.id) is None:
        #    log.Info("lane:"+self.ApolloName+"cannot find lane id:"+id)
        #</debug>
        return self.lanes.getLaneById(id)
    
    def parse(self,map,laneCounter,id):
        self.ApolloId=str(id)
        self.ApolloName='road_'+self.ApolloId
        if self.junction is not None:
            self.junction=map.findJunctionById(self.junction)
        if self.predecessor is not None:
            link=self.predecessor
            if link.elementType=='road':
                link.setPtr(map.findRoadById(link.elementId))
            elif link.elementType=='junction':
                link.setPtr(map.findJunctionById(link.elementId))
            else:
                log.warning("unknown link type")
        if self.successor is not None:
            link=self.successor
            if link.elementType=='road':
                link.setPtr(map.findRoadById(link.elementId))
            elif link.elementType=='junction':
                link.setPtr(map.findJunctionById(link.elementId))
            else:
                log.warning("unknown link type")

        self.lanes.parse(self,self.predecessor,self.successor,map,laneCounter)
        self.planView.parse(map)
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
        laneCounter=Counter()
        id=0
        for road in self.roads.values():
            road.parse(map,laneCounter,id)
            id+=1
        
    def print(self):
        for road in self.roads.values():
            road.print()

    