from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs

class Controller:
    def __init__(self,node):
        self.name=node.getAttribute('name')
        self.id=node.getAttribute('id')
        self.sequence=node.getAttribute('sequence')
        #log.info("controller id "+str(self.id))
        subDict=sub2dict(node)
        self.controls=[]
        
        controlList=subDict['control']
        for control in controlList:
            self.controls.append(control.getAttribute('signalId'))
        
class Controllers:
    def __init__(self,nodeList):
        self.controllers=dict()
        for node in nodeList:
            id=node.getAttribute('id')
            self.controllers[id]=Controller(node)