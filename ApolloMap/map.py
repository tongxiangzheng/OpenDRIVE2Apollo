from loguru import logger as log
import ApolloMap.proto_lib.modules.map.proto.map_pb2 as map_pb2
import pyproj
from ApolloMap.curve import Curve,OffsetsDict
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
            dist.id.id=junction.ApolloName
            self.setpolygon(dist,junction)
    def setSegment(self,planView,offsetsDict,segment):
        curve=Curve(planView,offsetsDict,self.transformer)
        for point in curve.points:
            dictPoint=segment.line_segment.point.add()
            dictPoint.x=point.x
            dictPoint.y=point.y

    def setLaneFromLane(self,lane,planView,offsetsDict):
        dist=self.map.lane.add()
        dist.id.id=lane.ApolloName
        if lane.forward==1:
            segment=dist.left_boundary.curve.segment.add()
            self.setSegment(planView,offsetsDict,segment)

            offsetsDict.addOffsets(lane.widthOffsets,-0.5)
            segment=dist.central_curve.segment.add()
            self.setSegment(planView,offsetsDict,segment)
            offsetsDict.popOffsets()

            offsetsDict.addOffsets(lane.widthOffsets,-1)
            segment=dist.right_boundary.curve.segment.add()
            self.setSegment(planView,offsetsDict,segment)
            offsetsDict.popOffsets()

        elif lane.forward==-1:
            segment=dist.right_boundary.curve.segment.add()
            self.setSegment(planView,offsetsDict,segment)

            offsetsDict.addOffsets(lane.widthOffsets,0.5)
            segment=dist.central_curve.segment.add()
            self.setSegment(planView,offsetsDict,segment)
            offsetsDict.popOffsets()

            offsetsDict.addOffsets(lane.widthOffsets,1)
            segment=dist.left_boundary.curve.segment.add()
            self.setSegment(planView,offsetsDict,segment)
            offsetsDict.popOffsets()
        else:
            log.error("unknown forward")
            


            
            "continue"
        if lane.type=='shoulder':
            dist.type=dist.LaneType.SHOULDER
        elif lane.type=='border':
            log.warning('translate:lane:not support lane type:border')
        elif lane.type=='driving':
            dist.type=dist.LaneType.CITY_DRIVING
        elif lane.type=='stop':
            log.warning('translate:lane:not support lane type:stop')
        elif lane.type=='none':
            dist.type=dist.LaneType.NONE
        elif lane.type=='restricted':
            log.warning('translate:lane:not support lane type:restricted')
        elif lane.type=='parking':
            dist.type=dist.LaneType.PARKING
        elif lane.type=='median':
            log.warning('translate:lane:not support lane type:median')
        elif lane.type=='biking':
            dist.type=dist.LaneType.BIKING
        elif lane.type=='sidewalk':
            dist.type=dist.LaneType.SIDEWALK
        elif lane.type=='curb':
            log.warning('translate:lane:not support lane type:curb')
        elif lane.type=='exit':
            log.warning('translate:lane:not support lane type:exit')
        elif lane.type=='entry':
            log.warning('translate:lane:not support lane type:entry')
        elif lane.type=='onramp':
            log.warning('translate:lane:not support lane type:onramp')
        elif lane.type=='offRamp':
            log.warning('translate:lane:not support lane type:offRamp')
        elif lane.type=='connectingRamp':
            log.warning('translate:lane:not support lane type:connectingRamp')
        else:
            log.warning('translate:lane:not known lane type:'+lane.type)
            
            
        dist.direction=dist.LaneDirection.FORWARD
        for predecessor in lane.ApolloPredecessors:
            id=dist.predecessor_id.add()
            id.id=predecessor.ApolloName
        for successor in lane.ApolloSuccessors:
            id=dist.successor_id.add()
            id.id=successor.ApolloName
        if lane.left_neighbor_forward_lane is not None:
            id=dist.left_neighbor_forward_lane_id.add()
            id.id=lane.left_neighbor_forward_lane.ApolloName
        if lane.left_neighbor_reverse_lane is not None:
            id=dist.left_neighbor_reverse_lane_id.add()
            id.id=lane.left_neighbor_reverse_lane.ApolloName
        if lane.right_neighbor_reverse_lane is not None:
            id=dist.right_neighbor_reverse_lane_id.add()
            id.id=lane.right_neighbor_reverse_lane.ApolloName
        if lane.right_neighbor_forward_lane is not None:
            id=dist.right_neighbor_forward_lane_id.add()
            id.id=lane.right_neighbor_forward_lane.ApolloName
        
            
         
         
    def setLaneFromRoad(self,openDriveRoad):
        left="1"
        leftOffsetsDict=OffsetsDict()
        while left in openDriveRoad.lanes.lanes:
            lane=openDriveRoad.lanes.lanes[left]
            self.setLaneFromLane(lane,openDriveRoad.planView,leftOffsetsDict)
            leftOffsetsDict.addOffsets(lane.widthOffsets,1)
            left=str(int(left)+1)
        right="-1"
        rightOffsetsDict=OffsetsDict()
        while right in openDriveRoad.lanes.lanes:
            lane=openDriveRoad.lanes.lanes[right]
            self.setLaneFromLane(lane,openDriveRoad.planView,rightOffsetsDict)
            rightOffsetsDict.addOffsets(lane.widthOffsets,-1)
            right=str(int(right)-1)
        
        #for lane in openDriveRoad.lanes.lanes.values():
        #    self.setLaneFromLane(lane,openDriveRoad.planView,OffsetsDict())

    def setLane(self,openDriveMap):
        for road in openDriveMap.roads.roads.values():
            self.setLaneFromRoad(road)

    def setRoad(self,openDriveMap):
        for road in openDriveMap.roads.roads.values():
            distRoad=self.map.road.add()
            distRoad.id.id=road.ApolloName
            section=distRoad.section.add()
            section.id.id="1"
            for lane in road.lanes.lanes.values():
                distLane=section.lane_id.add()
                distLane.id=lane.ApolloName
                "continue"
            if road.junction is not None:
                distRoad.junction_id.id=road.junction.ApolloName
            #distRoad.type=distRoad.Type.CITY_ROAD
    def parse_from_OpenDrive(self, openDriveMap):
        self.setHeader(openDriveMap)
        #setCrossWalk(openDriveMap)
        self.setJunction(openDriveMap)
        self.setLane(openDriveMap)
        self.setRoad(openDriveMap)
        
	