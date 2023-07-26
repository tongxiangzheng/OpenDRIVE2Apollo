import xml.dom.minidom

import OpenDriveMap.map
import ApolloMap.map
#import xml.dom.minidom

doc=xml.dom.minidom.parse("../../OpenDrive-maps-from-CARLA/carla_Town10HD_Opt.xodr")
openDriveMap=OpenDriveMap.map.OpenDriveMap(doc)
#openDriveMap.print()
ApolloMap=ApolloMap.map.ApolloMap()
ApolloMap.parse_from_OpenDrive(openDriveMap)
print(ApolloMap.map)





#with open("../../Apollo-maps/map/borregas_ave/base_map.bin", 'rb') as f:
#    gps_map = ApolloMap.parser.MapParser()
#    gps_map.parse_from_bin(f.read())
#    print(gps_map.map.header.version)