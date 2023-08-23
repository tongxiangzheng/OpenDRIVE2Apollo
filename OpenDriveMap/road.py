from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs,Counter

from OpenDriveMap.planView import PlanView,Offsets
from OpenDriveMap.signal import Signals

#import traceback

class RoadLink:
    def __init__(self,node,type='node'):
        #print(node)
        if type != 'node':
            self.elementType='road'
            self.sectionPtr=node
            return
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
    def setSectionByRoad(self,road):
        self.sectionPtr=road.getLaneSection(self.contactPoint)
    def setJunction(self,ptr):
        self.junctionPtr=ptr
    def print(self):
        print(self.elementType)
        if self.elementType=='road':
            print(self.sectionPtr)
        else:
            print(self.junctionPtr)
class Speed:
    def __init__(self,node):
        self.max=node.getAttribute('max')
        self.unit=node.getAttribute('unit')
        
class Type:
    def __init__(self,node):
        self.type=node.getAttribute('type')
        speedNodes=node.getElementsByTagName('speed')
        if len(speedNodes)==1:
            self.speed=Speed(speedNodes[0])
        
    
        
class LaneLink:
    def __init__(self,node):
        #print(node)
        self.id=node.getAttribute('id')
    #     self.ptr=None
    # def setPtr(self,ptr):
    #     self.ptr=ptr

class Overlap_junction_lane:
    def __init__(self,junction,lane):
        self.kind="junction_with_lane"
        junction.overlap_junction_lanes.append(self)
        lane.overlap_junction_lane=self
        self.junction=junction
        self.lane=lane
    def getApolloName(self):
        ApolloName='overlap_junction_I0_J'+self.junction.ApolloId+'_lane_'+self.lane.ApolloId
        return ApolloName
class Lane:
    def __init__(self,node):
        #dfs(node,1)
        self.id=node.getAttribute('id')
        self.type=node.getAttribute('type')
        
        if int(self.id)>0:
            self.forward=-1
        else:
            self.forward=1
            
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
        self.overlap_signal_lanes=[]
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
        self.widthOffsets=Offsets()
        self.widthOffsets.addOffsets(subDict['width'])

    def addConnect(self,lane,contactPoint):
        if lane is None:
            log.warning("lane is None")
            return
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
            log.error("unknown contactPoint: "+contactPoint)
    def addPredecessor(self,predecessor):
        if predecessor is None:
            log.warning("lane is None")
            #return
        if predecessor not in self.ApolloPredecessors:
            self.ApolloPredecessors.append(predecessor)
    def addSuccessor(self,successor):
        if successor is None:
            log.warning("lane is None")
            #return
        if successor not in self.ApolloSuccessors:
            self.ApolloSuccessors.append(successor)

    def parse(self,curRoad,preLink,sucLink,leftLane,rightLane,map,laneCounter,laneSectionId,s,t):
        self.ApolloId=laneCounter.getId()
        
        self.ApolloName='lane_'+self.ApolloId
        self.fullName='lane_'+curRoad.id+"_"+str(laneSectionId)+"_"+self.id
        #self.ApolloName=self.fullName
        
        self.s=s
        self.t=t
        self.widthOffsets.setStart(s)
        #self.ApolloName=self.fullName
        #log.debug("parsing lane "+self.fullName)
        
        #self.ApolloName='lane_'+curRoad.id+"_"+self.id
        # self.ApolloName=self.ApolloName.replace("-", "9")
        
        if self.forward<0:
            preLink,sucLink=sucLink,preLink     #swap
            #leftLane,rightLane=rightLane,leftLane
            self.predecessor,self.successor=self.successor,self.predecessor

        self.junction=curRoad.junction
        if self.junction is not None:
            map.addOverlap(Overlap_junction_lane(self.junction,self))
        self.road=curRoad

        if leftLane is not None:
            if int(self.id)*int(leftLane.id)<0:
                self.left_neighbor_reverse_lane=leftLane
            else:
                self.left_neighbor_forward_lane=leftLane
        if rightLane is not None:
            if self.forward*rightLane.forward<0:
                self.right_neighbor_reverse_lane=rightLane
            else:
                self.right_neighbor_forward_lane=rightLane

        if self.predecessor is not None:
            if preLink is not None and preLink.elementType=='road':
                preSection=preLink.sectionPtr
                predecessor=preSection.getLaneByLaneLink(self.predecessor)
                if predecessor is not None:
                    self.addPredecessor(predecessor)
                    if self.junction is not None:
                        #log.debug(predecessor.ApolloName+" add (maybe)suc lane:"+self.ApolloName+" as "+preLink.contactPoint)
                        predecessor.addConnect(self,preLink.contactPoint)
                else:
                    log.warning(self.fullName+": predecessor lane is none")
            else:
                log.error("parse: lane id:"+'lane_'+curRoad.id+"_"+self.id+" should have one road as pre")
                
        else:
            if preLink is not None and preLink.elementType=='junction':
                preJunction=preLink.junctionPtr
                predecessors=preJunction.getIncomingLane(curRoad,self)
                for predecessor in predecessors:
                    if predecessor is None:
                        log.warning("lane from junction is None")
                    self.addPredecessor(predecessor)
            else:
                pass
                #log.info("parse: lane id:"+'lane_'+curRoad.id+"_"+self.id+" may should have one junction as pre")
                

        if self.successor is not None:
            if sucLink is not None and sucLink.elementType=='road':
                sucSection=sucLink.sectionPtr
                successor=sucSection.getLaneByLaneLink(self.successor)
                if successor is not None:
                    self.addSuccessor(successor)
                    if self.junction is not None:
                        #log.debug(successor.ApolloName+"add (maybe)pre lane:"+self.ApolloName)
                        successor.addConnect(self,sucLink.contactPoint)
                else:
                    log.warning(self.fullName+": successor lane is none")

            else:
                log.error("parse: lane id:"+'lane_'+curRoad.id+"_"+self.id+" should have one road as suc")
                
        else:
            if sucLink is not None and sucLink.elementType=='junction':
                sucJunction=sucLink.junctionPtr
                successors=sucJunction.getConnectingLane(curRoad,self)
                for successor in successors:
                    if successor is None:
                        log.warning("lane from junction is None")
                    self.addSuccessor(successor)
            else:
                pass
                #log.info("parse: lane id:"+'lane_'+curRoad.id+"_"+self.id+" may should have one junction as suc")
        
            
    def print(self):
        print("  "+self.ApolloName)
        if self.predecessor is not None:
            print("    predecessor:"+self.predecessor.ptr.ApolloName)
        if self.successor is not None:
            print("    successor:"+self.successor.ptr.ApolloName)

class LanesSection:
    def __init__(self,node):
        self.lanes=dict()
        subDict=sub2dict(node)
        self.s=float(node.getAttribute('s'))
        leftList=subDict['left']
        if len(leftList)==1:
            lanes=leftList[0].getElementsByTagName('lane')
            for lane in lanes:
                id=lane.getAttribute('id')
                self.lanes[id]=Lane(lane)
        rightList=subDict['right']
        if len(rightList)==1:
            lanes=rightList[0].getElementsByTagName('lane')
            for lane in lanes:
                id=lane.getAttribute('id')
                self.lanes[id]=Lane(lane)
    
    def getLaneById(self,id):
        if id in self.lanes:
            return self.lanes[id]
        if id!='.':
            log.error(" cannot find id:"+id)
            #traceback.print_stack()
        return None
    def getLaneByLaneLink(self,laneLink):
        return self.getLaneById(laneLink.id)
    def parse(self,curRoad,preLink,sucLink,map,laneCounter,laneSectionId,s,t):
        lis=list(self.lanes)
        lis.append(".")
        for j in range(len(lis)):
            id=lis[j]
            if id=='.':
                break
            lane=self.getLaneById(id)
            leftLane=None
            rightLane=None
            if lane.forward<0:
                leftLane=self.getLaneById(lis[j+1]) #列表中id倒序，左侧车道id较小，所以在列表中较大下标位置
                rightLane=self.getLaneById(lis[j-1])
            else:
                leftLane=self.getLaneById(lis[j-1])
                rightLane=self.getLaneById(lis[j+1])
            lane.parse(curRoad,preLink,sucLink,leftLane,rightLane,map,laneCounter,laneSectionId,s,t)

class SanesSections:
    def __init__(self,node):
        subDicts=sub2dict(node)
        self.laneOffsets=Offsets()
        self.laneOffsets.addOffsets(subDicts['laneOffset'])
        self.lanesSections=[]
        self.road=None
        for laneSection in subDicts['laneSection']:
            self.lanesSections.append(LanesSection(laneSection))
            

    def getLaneById(self,i,id):
        if id in self.lanesSections[i]:
            return self.lanesSections[i].lanes[id]
        if id!='.':
            log.error(" cannot find id:"+i+'_'+id)
            #traceback.print_stack()
        return None
    
    def parse(self,curRoad,preLink,sucLink,map,laneCounter,roadLength):#当前road，当前road的前驱，当前road的后继
        self.road=curRoad
        for i in range(len(self.lanesSections)):
            lanesSection=self.lanesSections[i]
            preSection=None
            sucSection=None
            s=lanesSection.s
            t=roadLength
            if i==0:
                preSection=preLink
            else:
                preSection=RoadLink(self.lanesSections[i-1],'section')
                preSection.contactPoint='end'
            if i+1==len(self.lanesSections):
                sucSection=sucLink
                t=roadLength
            else:
                sucSection=RoadLink(self.lanesSections[i+1],'section')
                sucSection.contactPoint='start'
                t=self.lanesSections[i+1].s
            lanesSection.parse(curRoad,preSection,sucSection,map,laneCounter,i,s,t)
            
    def print(self):
        for lane in self.lanes:
            lane.print()


class Road:
    def __init__(self,node,map):
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
        self.lanes=SanesSections(laneList[0])

        signalList=subDict['signals']
        self.signals=None
        if len(signalList)==1:
            self.signals=Signals(signalList[0],self,map)


        # if len(signalList)==1:
        #     signalReferences=signalList[0].getElementsByTagName('signalReference')
        #     self.signalReferences=SignalReferences(signalReferences)
        

    def getLaneSection(self,contactPoint):
        if contactPoint=='start':
            return self.lanes.lanesSections[0]
        elif contactPoint=='end':
            return self.lanes.lanesSections[-1]
        else:
            log.error("unknown contactPoint: "+contactPoint)

    def getLaneById(self,id,contactPoint):
        laneSection=self.getLaneSection(contactPoint)
        ans=laneSection.getLaneById(id)
        #<debug>
        if ans is None:
            log.info("road:"+self.id+" cannot find lane id:"+id)
        #</debug>
        return ans
    
    def getLaneByLaneLink(self,laneLink,contactPoint):
        return self.getLaneById(laneLink.id,contactPoint)
        # laneSection=self.getLaneSection(contactPoint)
        # ans=laneSection.getLaneById(laneLink.id)
        # #<debug>
        # if ans is None:
        #     log.info("road:"+self.id+" cannot find lane id:"+laneLink.id)
        # #</debug>
        # return ans
    def checkContactPoint(self,junction):
        if self.predecessor is not None and self.predecessor.elementType=='junction' and self.predecessor.elementId==junction.id:
            return 'start'
        if self.successor is not None and self.successor.elementType=='junction' and self.successor.elementId==junction.id:
            return 'end'
        log.warning("road: "+self.id+" cannot determine contactPoint from junction: "+junction.id)
        return None
    def parse(self,map,laneCounter,signalCounter,id):
        self.ApolloId=str(id)
        self.ApolloName='road_'+self.ApolloId
        if self.junction is not None:
            self.junction=map.findJunctionById(self.junction)
        if self.predecessor is not None:
            link=self.predecessor
            if link.elementType=='road':
                link.setSectionByRoad(map.findRoadById(link.elementId))
            elif link.elementType=='junction':
                link.setJunction(map.findJunctionById(link.elementId))
            else:
                log.warning("unknown link type")
        if self.successor is not None:
            link=self.successor
            if link.elementType=='road':
                link.setSectionByRoad(map.findRoadById(link.elementId))
            elif link.elementType=='junction':
                link.setJunction(map.findJunctionById(link.elementId))
            else:
                log.warning("unknown link type")
        self.roadLength=self.planView.getLength()
        self.lanes.parse(self,self.predecessor,self.successor,map,laneCounter,self.roadLength)
        self.planView.parse(map)
        if self.signals is not None:
            self.signals.parse(map,signalCounter)
    def print(self):
        print(self.ApolloName)
        self.lanes.print()

class Roads:
    def __init__(self,nodeList,map):
        self.roads=dict()
        for node in nodeList:
            id=node.getAttribute('id')
            #print(id)
            self.roads[id]=Road(node,map)

    def parse(self,map):
        laneCounter=Counter()
        signalCounter=Counter()
        id=0
        for road in self.roads.values():
            road.parse(map,laneCounter,signalCounter,id)
            id+=1
        
    def print(self):
        for road in self.roads.values():
            road.print()

    