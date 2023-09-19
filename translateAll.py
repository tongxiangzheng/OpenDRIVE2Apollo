import xml.dom.minidom

import OpenDriveMap.map
import ApolloMap.map
from loguru import logger as log
import ApolloMap.proto_lib.modules.map.proto.map_pb2 as map_pb2
def translate(fromPath,toPath):
  doc=xml.dom.minidom.parse(fromPath)
  openDriveMap=OpenDriveMap.map.OpenDriveMap(doc)
  apolloMap=ApolloMap.map.ApolloMap(openDriveMap)
  with open(toPath+'.txt', "w",encoding='utf-8') as f:
    print(apolloMap.map,file=f)
  with open(toPath+'.bin', "wb") as f:
    f.write(apolloMap.map.SerializeToString())

def tryAll():
  log.info("translate map 01")
  translate("OpenDrive-maps-from-CARLA/carla_Town01.xodr","mapData/Town01")
  log.info("translate map 02")
  translate("OpenDrive-maps-from-CARLA/carla_Town02.xodr","mapData/Town02")
  log.info("translate map 03")
  translate("OpenDrive-maps-from-CARLA/carla_Town03.xodr","mapData/Town03")
  log.info("translate map 04")
  translate("OpenDrive-maps-from-CARLA/carla_Town04.xodr","mapData/Town04")
  log.info("translate map 05")
  translate("OpenDrive-maps-from-CARLA/carla_Town05.xodr","mapData/Town05")
  log.info("translate map 06")
  translate("OpenDrive-maps-from-CARLA/carla_Town06.xodr","mapData/Town06")
  log.info("translate map 07")
  translate("OpenDrive-maps-from-CARLA/carla_Town07.xodr","mapData/Town07")
  log.info("translate map 10HD")
  translate("OpenDrive-maps-from-CARLA/carla_Town10HD.xodr","mapData/Town10HD_Opt")
  log.info("translate map 11")
  translate("OpenDrive-maps-from-CARLA/carla_Town11_Town11.xodr","mapData/Town11")
  log.info("translate map 12")
  translate("OpenDrive-maps-from-CARLA/carla_Town12_Town12.xodr","mapData/Town12")

def cp(pathFrom,pathTo):
  with open(pathTo, "wb") as fw:
    with open(pathFrom, "rb") as fr:
      fw.write(fr.read())
def toComOpT(path):
  translate(path,"01")
  cp("01.bin","F:/ComOpT/scripts/comopt/data/map/openDriveTest/base_map.bin")
  cp("01.bin","F:/ComOpT/scripts/comopt/data/map/openDriveTest/svl_map.bin")

def toApollo(path):
  translate(path,"01")
  cp("01.bin","/home/txz/dockerMap/opendrive_test/base_map.bin")
  cp("01.txt","/home/txz/dockerMap/opendrive_test/base_map.txt")

tryAll()