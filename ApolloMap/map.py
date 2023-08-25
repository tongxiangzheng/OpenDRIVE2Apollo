from loguru import logger as log
import ApolloMap.proto_lib.modules.map.proto.map_pb2 as map_pb2
import ApolloMap.proto_lib.modules.map.proto.map_overlap_pb2 as map_overlap_pb2
import pyproj
from ApolloMap.curve import Curve,OffsetsDict,RoadPoint
class ApolloMap:
    def __init__(self,openDriveMap):
        self.map=map_pb2.Map()
        self.parse_from_OpenDrive(openDriveMap)
        
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

    #abandon
    def setpolygon(self,dist,junction):
        for connection in junction.connections:
            for lane in connection.laneLinks:
                "to be continued..."
            #pb_point = dist.polygon.point.add()

            #pb_point.x, pb_point.y, pb_point.z = x, y, 0

    def setJunction(self,openDriveMap):
    
        for junction in openDriveMap.junctions.junctions.values():
            dist=self.map.junction.add()
            dist.id.id=junction.ApolloName
            #self.setpolygon(dist,junction)
            for overlap_junction_lane in junction.overlap_junction_lanes:
                distOverlap=dist.overlap_id.add()
                distOverlap.id=overlap_junction_lane.getApolloName()
            for overlap_junction_signal in junction.overlap_junction_signals:
                distOverlap=dist.overlap_id.add()
                distOverlap.id=overlap_junction_signal.getApolloName()

    def setSegment(self,lane,planView,offsetsDict,segment,notes):
        curve=Curve(planView,offsetsDict,lane,self.transformer,notes)
        for point in curve.points:
            dictPoint=segment.line_segment.point.add()
            dictPoint.x=point.x
            dictPoint.y=point.y
            #log.info(str(point.x)+' '+str(point.y))
        segment.s=0.0
        segment.start_position.x=curve.points[0].x
        segment.start_position.y=curve.points[0].y
        segment.start_position.x=0.0
        
        segment.length=curve.getLength()
        #log.info("----------------------")

    def setLaneFromLane(self,lane,planView,offsetsDict):
        dist=self.map.lane.add()
        dist.id.id=lane.ApolloName
        if lane.forward==1:
            segment=dist.left_boundary.curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"left")

            offsetsDict.addOffsets(lane.widthOffsets,-0.5)
            segment=dist.central_curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"central")
            offsetsDict.popOffsets()

            offsetsDict.addOffsets(lane.widthOffsets,-1)
            segment=dist.right_boundary.curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"right")
            offsetsDict.popOffsets()

        elif lane.forward==-1:
            segment=dist.right_boundary.curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"right")

            offsetsDict.addOffsets(lane.widthOffsets,0.5)
            segment=dist.central_curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"central")
            offsetsDict.popOffsets()

            offsetsDict.addOffsets(lane.widthOffsets,1)
            segment=dist.left_boundary.curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"left")
            offsetsDict.popOffsets()
        else:
            log.error("unknown forward")
            

        if lane.type=='shoulder':
            dist.type=dist.LaneType.SHOULDER
        elif lane.type=='border':
            dist.type=dist.LaneType.SHOULDER
        elif lane.type=='driving':
            dist.type=dist.LaneType.CITY_DRIVING
        elif lane.type=='stop':
            log.info('translate:lane:not support lane type:stop')
        elif lane.type=='none':
            dist.type=dist.LaneType.NONE
        elif lane.type=='restricted':
            log.info('translate:lane:not support lane type:restricted')
        elif lane.type=='parking':
            dist.type=dist.LaneType.PARKING
        elif lane.type=='median':
            #log.warning('translate:lane:not support lane type:median')
            dist.type=dist.LaneType.SHOULDER
        elif lane.type=='biking':
            dist.type=dist.LaneType.BIKING
        elif lane.type=='sidewalk':
            dist.type=dist.LaneType.SIDEWALK
        elif lane.type=='curb':
            log.info('translate:lane:not support lane type:curb')
        elif lane.type=='exit':
            log.info('translate:lane:not support lane type:exit')
        elif lane.type=='entry':
            log.info('translate:lane:not support lane type:entry')
        elif lane.type=='onramp':
            log.info('translate:lane:not support lane type:onramp')
        elif lane.type=='offRamp':
            log.info('translate:lane:not support lane type:offRamp')
        elif lane.type=='connectingRamp':
            log.info('translate:lane:not support lane type:connectingRamp')
        elif lane.type=='bidirectional':
            dist.type=dist.LaneType.CITY_DRIVING
        else:
            log.info('translate:lane:not known lane type:'+lane.type)
        
        if lane.overlap_junction_lane is not None:
            distOverlap=dist.overlap_id.add()
            distOverlap.id=lane.overlap_junction_lane.getApolloName()
        for overlap_signal_lane in lane.overlap_signal_lanes:
            distOverlap=dist.overlap_id.add()
            distOverlap.id=overlap_signal_lane.getApolloName()

        if lane.type!='bidirectional':
            dist.direction=dist.LaneDirection.FORWARD
        else:
            dist.direction=dist.LaneDirection.BIDIRECTION


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
        
            
         
         
    def setLaneFromLanesSection(self,openDriveRoad,lanesSection,midOffsets):
        left="1"
        leftOffsetsDict=OffsetsDict()
        leftOffsetsDict.addOffsets(midOffsets,1)
        while left in lanesSection.lanes:
            lane=lanesSection.lanes[left]
            self.setLaneFromLane(lane,openDriveRoad.planView,leftOffsetsDict)
            leftOffsetsDict.addOffsets(lane.widthOffsets,-1*lane.forward)
            left=str(int(left)+1)
        right="-1"
        rightOffsetsDict=OffsetsDict()
        rightOffsetsDict.addOffsets(midOffsets,1)
        while right in lanesSection.lanes:
            lane=lanesSection.lanes[right]
            self.setLaneFromLane(lane,openDriveRoad.planView,rightOffsetsDict)
            rightOffsetsDict.addOffsets(lane.widthOffsets,-1*lane.forward)
            right=str(int(right)-1)
    def setLaneFromRoad(self,openDriveRoad):
        midOffsets=openDriveRoad.lanes.laneOffsets
        # if openDriveRoad.id=='782':
        #     print("midOffsets:")
        #     midOffsets.print()
        #     print("0: ",midOffsets.getOffset(0))
            
        for laneSection in openDriveRoad.lanes.lanesSections:
            self.setLaneFromLanesSection(openDriveRoad,laneSection,midOffsets)

    def setLane(self,openDriveMap):
        for road in openDriveMap.roads.roads.values():
            self.setLaneFromRoad(road)

    def setRoad(self,openDriveMap):
        for road in openDriveMap.roads.roads.values():
            distRoad=self.map.road.add()
            distRoad.id.id=road.ApolloName
            section=distRoad.section.add()
            section.id.id="1"
            for lanesSection in road.lanes.lanesSections:
                for lane in lanesSection.lanes.values():
                    distLane=section.lane_id.add()
                    distLane.id=lane.ApolloName
                    "continue"
            if road.junction is not None:
                distRoad.junction_id.id=road.junction.ApolloName
            #distRoad.type=distRoad.Type.CITY_ROAD
    def setSignal(self,openDriveMap):
        for signal in openDriveMap.signals.values():
            distSignal=self.map.signal.add()
            distSignal.type=distSignal.Type.MIX_3_VERTICAL
            distSignal.id.id=signal.ApolloName
            for overlap_signal_lane in signal.overlap_signal_lanes:
                distOverlap=distSignal.overlap_id.add()
                distOverlap.id=overlap_signal_lane.getApolloName()
            if signal.overlap_junction_signal is not None:
                distOverlap=distSignal.overlap_id.add()
                distOverlap.id=signal.overlap_junction_signal.getApolloName()
            roadPoint=RoadPoint(signal.road.planView,signal.s,signal.t,self.transformer)

            distPoint=distSignal.boundary.point.add()
            distPoint.x=roadPoint.point.x-5.0
            distPoint.y=roadPoint.point.y-5.0
            distPoint.z=0.0
            
            distPoint=distSignal.boundary.point.add()
            distPoint.x=roadPoint.point.x+5.0
            distPoint.y=roadPoint.point.y-5.0
            distPoint.z=0.0
            
            distPoint=distSignal.boundary.point.add()
            distPoint.x=roadPoint.point.x+5.0
            distPoint.y=roadPoint.point.y+5.0
            distPoint.z=0.0
            
            distPoint=distSignal.boundary.point.add()
            distPoint.x=roadPoint.point.x-5.0
            distPoint.y=roadPoint.point.y+5.0
            distPoint.z=0.0
            distStopLine=distSignal.stop_line.add()
            distStopLineSegment=distStopLine.segment.add()

            distStopLinePoint=distStopLineSegment.line_segment.point.add()
            roadPoint.Offset(3)
            distStopLinePoint.x=roadPoint.point.x
            distStopLinePoint.y=roadPoint.point.y
            distStopLinePoint.z=0.0

            distStopLinePoint=distStopLineSegment.line_segment.point.add()
            roadPoint.Offset(-3)
            distStopLinePoint.x=roadPoint.point.x
            distStopLinePoint.y=roadPoint.point.y
            distStopLinePoint.z=0.0

            distStopLinePoint=distStopLineSegment.line_segment.point.add()
            roadPoint.Offset(-3)
            distStopLinePoint.x=roadPoint.point.x
            distStopLinePoint.y=roadPoint.point.y
            distStopLinePoint.z=0.0
            
            subSignal0=distSignal.subsignal.add()
            subSignal0.id.id="0"
            subSignal0.type=subSignal0.Type.CIRCLE
            subSignal0.location.x=roadPoint.point.x
            subSignal0.location.y=roadPoint.point.y
            subSignal0.location.z=0.0

            subSignal1=distSignal.subsignal.add()
            subSignal1.id.id="1"
            subSignal1.type=subSignal0.Type.CIRCLE
            subSignal1.location.x=roadPoint.point.x
            subSignal1.location.y=roadPoint.point.y
            subSignal1.location.z=1.0
            
            subSignal2=distSignal.subsignal.add()
            subSignal2.id.id="2"
            subSignal2.type=subSignal0.Type.CIRCLE
            subSignal2.location.x=roadPoint.point.x
            subSignal2.location.y=roadPoint.point.y
            subSignal2.location.z=2.0
            
                
    def setOverlapLaneObject(self,distOverlap,lane):
        distLane=distOverlap.object.add()
        distLane.id.id=lane.ApolloName
        distLane.lane_overlap_info.start_s=float(0)
        distLane.lane_overlap_info.end_s=float(1)   #先这样填吧...
        distLane.lane_overlap_info.is_merge=False

    def setOverlapJunctionObject(self,distOverlap,junction):
        distJunction=distOverlap.object.add()
        distJunction.id.id=junction.ApolloName
        distJunction.junction_overlap_info.CopyFrom(map_overlap_pb2.JunctionOverlapInfo())  #nt设计
    
    def setOverlapSignalObject(self,distOverlap,signal):
        distSignal=distOverlap.object.add()
        distSignal.id.id=signal.ApolloName
        distSignal.signal_overlap_info.CopyFrom(map_overlap_pb2.SignalOverlapInfo())  #nt设计
    
    
    def setOverlap(self,openDriveMap):
        for overlap in openDriveMap.overlaps:
            distOverlap=self.map.overlap.add()
            if overlap.kind=="junction_with_lane":
                distOverlap.id.id=overlap.getApolloName()
                self.setOverlapJunctionObject(distOverlap,overlap.junction)
                self.setOverlapLaneObject(distOverlap,overlap.lane)

            elif overlap.kind=="signal_with_lane":
                distOverlap.id.id=overlap.getApolloName()
                self.setOverlapSignalObject(distOverlap,overlap.signal)
                self.setOverlapLaneObject(distOverlap,overlap.lane)

            elif overlap.kind=="junction_with_signal":
                distOverlap.id.id=overlap.getApolloName()
                self.setOverlapJunctionObject(distOverlap,overlap.junction)
                self.setOverlapSignalObject(distOverlap,overlap.signal)

            else:
                log.error("unknown overlap kind: "+overlap.kind)
    def parse_from_OpenDrive(self,openDriveMap):
        self.sourceCrs=pyproj.CRS.from_proj4("+proj=utm +zone=32 +ellps=WGS84")
            #if proj data is empty,use "+proj=utm +zone={} +ellps=WGS84" by default
        self.distCrs=pyproj.CRS.from_proj4("+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
       
        self.setHeader(openDriveMap)
        #setCrossWalk(openDriveMap)
        self.setJunction(openDriveMap)
        self.setLane(openDriveMap)
        self.setRoad(openDriveMap)
        self.setSignal(openDriveMap)
        self.setOverlap(openDriveMap)
	