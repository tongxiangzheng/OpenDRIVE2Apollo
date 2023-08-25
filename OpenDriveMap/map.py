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
        self.overlaps=[]
        self.signals=dict()
        self.objects=[]
        
        self.header=header.Header(subDict['header'][0])
        self.roads=road.Roads(subDict['road'],self)
        #self.controllers=controller.Controllers(subDict['controller'])
        self.junctions=junction.Junctions(subDict['junction'])
        self.junctions.parse(self)
        self.roads.parse(self)

    def findRoadById(self,id):
        return self.roads.roads[id]
    def findJunctionById(self,id):
        return self.junctions.junctions[id]
    
    def addOverlap(self,overlap):
        self.overlaps.append(overlap)

    def print(self):
        self.roads.print()