import xml.dom.minidom
from OpenDriveMap import header
from OpenDriveMap import road
from OpenDriveMap import controller
from OpenDriveMap import junction
from OpenDriveMap.dom_tool import sub2dict
class Map:
    def __init__(self,document):
        root=document.documentElement
        subDict=sub2dict(root)
        
        self.header=header.Header(subDict['header'][0])
        self.roads=road.Roads(subDict['road'])
        self.controllers=controller.Controllers(subDict['controller'])
        self.junctions=junction.Junctions(subDict['junction'])
        