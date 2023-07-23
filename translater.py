from xml.dom.minidom import parse

import OpenDriveMap.map
#import xml.dom.minidom



doc=parse("../../OpenDrive-maps-from-CARLA/test.xodr")
map=OpenDriveMap.map.Map(doc)

