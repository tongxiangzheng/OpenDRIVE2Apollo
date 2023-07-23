from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs

class LaneLink:
    def __init__(self,node):
        self.laneLink_from=node.getAttribute('from')
        #from是关键词 :(
        self.laneLink_to=node.getAttribute('to')

class Connection:
    def __init__(self,node):
        self.id=node.getAttribute('id')
        self.incomingRoad=node.getAttribute('incomingRoad')
        self.connectingRoad=node.getAttribute('connectingRoad')
        self.contactPoint=node.getAttribute('contactPoint')
        #log.info("connection id "+str(self.id))
        self.laneLinks=[]
        for laneLink in node.getElementsByTagName('laneLink'):
            self.laneLinks.append(LaneLink(laneLink))
        
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
        log.info("junction id "+str(self.id))
        
        subDict=sub2dict(node)
        self.connections=[]
        self.controllers=[]
        
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
class Junctions:
    def __init__(self,nodeList):
        self.junctions=dict()
        for node in nodeList:
            id=node.getAttribute('id')
            #print(id)
            self.junctions[id]=Junction(node)