from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs

class LaneLink:
    def __init__(self,node,contactPoint):
        self.lane_from=node.getAttribute('from')
        #from是关键词 :(
        self.lane_to=node.getAttribute('to')
        self.contactPoint_from=None
        self.contactPoint_to=contactPoint
    def parse(self,map,incomingRoad,connectingRoad,junction):
        self.contactPoint_from=incomingRoad.checkContactPoint(junction)
        self.lane_from_ptr=incomingRoad.getLaneById(self.lane_from,self.contactPoint_from)
        if self.lane_from_ptr is None:
            log.warning("have no lane link from lane: "+incomingRoad.id+'_'+self.lane_from)
        self.lane_to_ptr=connectingRoad.getLaneById(self.lane_to,self.contactPoint_to)
        if self.lane_to_ptr is None:
            log.warning("have no lane link to lane: "+connectingRoad.id+'_'+self.lane_to)
class Connection:
    def __init__(self,node):
        self.id=node.getAttribute('id')
        self.incomingRoad=node.getAttribute('incomingRoad')
        self.connectingRoad=node.getAttribute('connectingRoad')
        self.contactPoint=node.getAttribute('contactPoint')
        self.incomingRoad_ptr=None
        self.connectingRoad_ptr=None
        #log.info("connection id "+str(self.id))
        self.laneLinks=[]
        for laneLink in node.getElementsByTagName('laneLink'):
            self.laneLinks.append(LaneLink(laneLink,self.contactPoint))
    def parse(self,map,junction):
        self.incomingRoad_ptr=map.findRoadById(self.incomingRoad)
        self.connectingRoad_ptr=map.findRoadById(self.connectingRoad)
        if self.incomingRoad_ptr is None:
            log.error("junction.connection:cannot find road")
        if self.connectingRoad_ptr is None:
            log.error("junction.connection:cannot find road")
        
        for laneLink in self.laneLinks:
            laneLink.parse(map,self.incomingRoad_ptr,self.connectingRoad_ptr,junction)
class Controller:
    def __init__(self,node):
        self.id=node.getAttribute('id')
        self.type=node.getAttribute('type')
        self.sequence=node.getAttribute('sequence')

class UserData:
    def __init__(self,node):
        if len(node.getElementsByTagName('vectorJunction'))==1:
            vectorJunction=node.getElementsByTagName('vectorJunction')[0]
            self.junctionId=vectorJunction.getAttribute('junctionId')
        else:
            log.info("junction.userData: no vectorJunction")
        
class Junction:
    def __init__(self,node):
        self.name=node.getAttribute('name')
        self.id=node.getAttribute('id')
        #log.info("junction id "+str(self.id))
        
        subDict=sub2dict(node)
        self.connections=[]
        self.controllers=[]
        self.overlap_junction_lanes=[]
        self.overlap_junction_signals=[]
        connectionList=subDict['connection']
        for connection in connectionList:
            self.connections.append(Connection(connection))

        controllerList=subDict['controller']
        for controller in controllerList:
            self.controllers.append(Controller(controller))

        
        if len(subDict['userData'])==1:
            self.userData=UserData(subDict['userData'][0])
        else:
            log.info("junction: no userData")
    #abandon
    def getConnectingRoad(self,road):
        ans=[]
        for connection in self.connections:
            if connection.incomingRoad==road.id:
                ans.append(connection.connectingRoad)
        return ans
    #abandon
    def getIncomingRoad(self,road):
        ans=[]
        for connection in self.connections:
            if connection.connectingRoad==road.id:
                ans.append(connection.incomingRoad)
        return ans
    
    def getConnectingLane(self,road,lane):
        ans=[]
        for connection in self.connections:
            if connection.incomingRoad_ptr==road:
                for laneLink in connection.laneLinks:
                    if laneLink.lane_from_ptr==lane:
                        ans.append(laneLink.lane_to_ptr)
            if connection.connectingRoad_ptr==road:
                for laneLink in connection.laneLinks:
                    if laneLink.lane_to_ptr==lane:
                        ans.append(laneLink.lane_from_ptr)
        return ans
    def getIncomingLane(self,road,lane):
        ans=[]
        for connection in self.connections:
            if connection.incomingRoad_ptr==road:
                for laneLink in connection.laneLinks:
                    if laneLink.lane_from_ptr==lane:
                        ans.append(laneLink.lane_to_ptr)
            if connection.connectingRoad_ptr==road:
                for laneLink in connection.laneLinks:
                    if laneLink.lane_to_ptr==lane:
                        ans.append(laneLink.lane_from_ptr)
        return ans
    
    def parse(self,map,id):
        self.ApolloId=str(id)
        self.ApolloName="J_"+self.ApolloId
        for connection in self.connections:
            connection.parse(map,self)

class Junctions:
    def __init__(self,nodeList):
        self.junctions=dict()
        for node in nodeList:
            id=node.getAttribute('id')
            #print(id)
            self.junctions[id]=Junction(node)
    def parse(self,map):
        id=0
        for junction in self.junctions.values():
            junction.parse(map,id)
            id+=1