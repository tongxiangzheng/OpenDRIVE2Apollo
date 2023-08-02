import xml.dom.minidom

import OpenDriveMap.map
import ApolloMap.map
#import xml.dom.minidom

doc=xml.dom.minidom.parse("../../OpenDrive-maps-from-CARLA/carla_Town01_Opt.xodr")
openDriveMap=OpenDriveMap.map.OpenDriveMap(doc)
#openDriveMap.print()
ApolloMap=ApolloMap.map.ApolloMap()
ApolloMap.parse_from_OpenDrive(openDriveMap)

with open("01.txt", "w",encoding='utf-8') as f:
  print(ApolloMap.map,file=f)






#with open("../../Apollo-maps/map/borregas_ave/base_map.bin", 'rb') as f:
#    gps_map = ApolloMap.parser.MapParser()
#    gps_map.parse_from_bin(f.read())
#    print(gps_map.map.header.version)