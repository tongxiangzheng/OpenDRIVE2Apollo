import xml.dom.minidom
from OpenDriveMap import header
from OpenDriveMap import road
from OpenDriveMap import controller
from OpenDriveMap import junction
from OpenDriveMap.dom_tool import sub2dict
from loguru import logger as log

class OpenDriveMap:
    def __init__(self,document):
        root=document.documentElement
        subDict=sub2dict(root)
        
        self.header=header.Header(subDict['header'][0])
        self.roads=road.Roads(subDict['road'])
        self.controllers=controller.Controllers(subDict['controller'])
        self.junctions=junction.Junctions(subDict['junction'])

        self.roads.parse(self)
        

    def findRoadByRoadLink(self,link):
        if link.elementType=='road':
            return self.roads.roads[link.elementId]
        elif link.elementType=='junction':
            return self.junctions.junctions[link.elementId]
        else:
            log.warning("unknown link type")
        return None
    def print(self):
        self.roads.print()