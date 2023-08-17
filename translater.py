import xml.dom.minidom

import OpenDriveMap.map
import ApolloMap.map
from loguru import logger as log
import ApolloMap.proto_lib.modules.map.proto.map_pb2 as map_pb2
def translate(fromPath,toPath):
  doc=xml.dom.minidom.parse(fromPath)
  openDriveMap=OpenDriveMap.map.OpenDriveMap(doc)
  apolloMap=ApolloMap.map.ApolloMap()
  apolloMap.parse_from_OpenDrive(openDriveMap)
  with open(toPath, "w",encoding='utf-8') as f:
    print(ApolloMap.map,file=f)

def tryAll():
  log.info("translate map 01")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town01.xodr","mapData/01.txt")
  log.info("translate map 02")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town02.xodr","mapData/02.txt")
  log.info("translate map 03")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town03.xodr","mapData/03.txt")
  log.info("translate map 04")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town04.xodr","mapData/04.txt")
  log.info("translate map 05")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town05.xodr","mapData/05.txt")
  log.info("translate map 06")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town06.xodr","mapData/06.txt")
  log.info("translate map 07")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town07.xodr","mapData/07.txt")
  log.info("translate map 10HD")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town10HD.xodr","mapData/10HD.txt")
  log.info("translate map 11")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town11_Town11.xodr","mapData/11.txt")
  log.info("translate map 12")
  translate("../../OpenDrive-maps-from-CARLA/carla_Town12_Town12.xodr","mapData/12.txt")
  








tryAll()
#mapPath="../../OpenDrive-maps-from-CARLA/carla_Town03.xodr"
#mapPath="../../OpenDrive-maps-from-CARLA/carla_Town11_Town11.xodr"
#mapPath="../../OpenDrive-maps-from-CARLA/spiral.xodr"
#doc=xml.dom.minidom.parse(mapPath)
#openDriveMap=OpenDriveMap.map.OpenDriveMap(doc)
#openDriveMap.print()
#ApolloMap=ApolloMap.map.ApolloMap()
#ApolloMap.parse_from_OpenDrive(openDriveMap)

#with open("01.txt", "w",encoding='utf-8') as f:
#  print(ApolloMap.map,file=f)
#with open("01.bin", "wb") as f:
#  f.write(ApolloMap.map.SerializeToString())

#with open("C:\\Users\\DELL\\ComOpT\\scripts\\comopt\\data\\map\\openDriveTest\\base_map.bin", "wb") as f:
#  f.write(ApolloMap.map.SerializeToString())
#with open("C:\\Users\\DELL\\ComOpT\\scripts\\comopt\\data\\map\\openDriveTest\\svl_map.bin", "wb") as f:
#  f.write(ApolloMap.map.SerializeToString())




  
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


# 1 对比确认地图是正确的，连接关系检测
#  识别十字路口
# 3 螺旋线
# 鲁棒性，能跑carla
# 2 signal clsswalk
# 