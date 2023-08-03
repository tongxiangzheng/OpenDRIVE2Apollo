import xml.dom.minidom

import OpenDriveMap.map
import ApolloMap.map
#import xml.dom.minidom
import ApolloMap.proto_lib.modules.map.proto.map_pb2 as map_pb2

doc=xml.dom.minidom.parse("../../OpenDrive-maps-from-CARLA/carla_Town01_Opt.xodr")
openDriveMap=OpenDriveMap.map.OpenDriveMap(doc)
#openDriveMap.print()
ApolloMap=ApolloMap.map.ApolloMap()
ApolloMap.parse_from_OpenDrive(openDriveMap)

with open("01.txt", "w",encoding='utf-8') as f:
  print(ApolloMap.map,file=f)

with open("C:\\Users\\DELL\\ComOpT\\scripts\\comopt\\data\\map\\openDriveTest\\base_map.bin", "wb") as f:
  f.write(ApolloMap.map.SerializeToString())
with open("C:\\Users\\DELL\\ComOpT\\scripts\\comopt\\data\\map\\openDriveTest\\svl_map.bin", "wb") as f:
  f.write(ApolloMap.map.SerializeToString())




  
# with open("01.bin","rb") as f:
#   txt=f.read()
#   map=map_pb2.Map()
#   map.ParseFromString(txt)
#   with open("02.bin", "wb") as f2:
#     f2.write(map.SerializeToString())





#with open("../../Apollo-maps/map/borregas_ave/base_map.bin", 'rb') as f:
#    gps_map = ApolloMap.parser.MapParser()
#    gps_map.parse_from_bin(f.read())
#    print(gps_map.map.header.version)