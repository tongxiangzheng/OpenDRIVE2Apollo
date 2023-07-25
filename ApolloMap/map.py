import ApolloMap.proto_lib.modules.map.proto.map_pb2 as map_pb2
import pyproj

class ApolloMap:
    def __init__(self):
        self.map=map_pb2.Map()
        
        self.sourceCrs=pyproj.CRS.from_proj4("+proj=utm +zone=32 +ellps=WGS84")
            #if proj data is empty,use "+proj=utm +zone={} +ellps=WGS84" by default
        self.distCrs=pyproj.CRS.from_proj4("+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
       
        
    def setProjection(self,projText):
        if projText is not None:
            self.sourceCrs=pyproj.CRS.from_proj4(projText)
        
            self.transformer = pyproj.Transformer.from_crs(self.sourceCrs, self.distCrs)
	

    def setHeader(self,openDriveMap):
        self.map.header.version=b"1.500000"
        self.map.header.date=str.encode(openDriveMap.header.date)
    
        self.map.header.projection.proj=str.encode("+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
        self.setProjection(openDriveMap.header.geoReference.data)
    
        self.map.header.district=b"0" #不知道作用
        self.map.header.rev_major=b"1"
        self.map.header.rev_minor=b"0"
    
        self.map.header.left=float(openDriveMap.header.west)
        self.map.header.top=float(openDriveMap.header.north)
        self.map.header.right=float(openDriveMap.header.east)
        self.map.header.bottom=float(openDriveMap.header.south)
        self.map.header.vendor=str.encode(openDriveMap.header.vendor)
    
    def setCrosswalk(self,openDriveMap):
        crosswalk0=self.crosswalk.add()
        "to be continued..."
    
    def setpolygon(self,dist,junction):
        for connection in junction.connections:
            for lane in connection.laneLinks:
                "to be continued..."
            #pb_point = dist.polygon.point.add()

            #pb_point.x, pb_point.y, pb_point.z = x, y, 0

    def setJunction(self,openDriveMap):
    
        for id,junction in openDriveMap.junctions.junctions.items():
            dist=self.map.junction.add()
            dist.id.id=id
            self.setpolygon(dist,junction)

    def parse_from_OpenDrive(self, openDriveMap):
        self.setHeader(openDriveMap)
        #setCrossWalk(openDriveMap)
        self.setJunction(openDriveMap)
    
        
	