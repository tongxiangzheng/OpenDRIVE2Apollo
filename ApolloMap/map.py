from loguru import logger as log
import os
import sys

LIBDIR = os.path.split(os.path.abspath(__file__))[0]

sys.path.insert(0,os.path.join(LIBDIR, 'proto_lib'))
import ApolloMap.proto_lib.modules.map.proto.map_pb2 as map_pb2
import ApolloMap.proto_lib.modules.map.proto.map_overlap_pb2 as map_overlap_pb2
import pyproj
from ApolloMap.curve import Curve,OffsetsDict,RoadPoint,Polygon,Point
class ApolloMap:
    def __init__(self,openDriveMap):
        self.map=map_pb2.Map()
        self.lanes=dict()
        self.parse_from_OpenDrive(openDriveMap)
        
    def setProjection(self,projText):
        if projText is not None:
            self.sourceCrs=pyproj.CRS.from_proj4(projText)
        
        self.transformer = pyproj.Transformer.from_crs(self.sourceCrs, self.distCrs)
	

    def setHeader(self,openDriveMap):
        self.map.header.version=b"1.500000"
        self.map.header.date=str.encode(openDriveMap.header.date)
    
        self.map.header.projection.proj=str.encode("+proj=utm +zone=10 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
        self.setProjection(openDriveMap.header.geoReference.data)
    
        self.map.header.district=b"0" #不知道作用
        self.map.header.rev_major=b"1"
        self.map.header.rev_minor=b"0"
    
        self.map.header.left=float(openDriveMap.header.west)
        self.map.header.top=float(openDriveMap.header.north)
        self.map.header.right=float(openDriveMap.header.east)
        self.map.header.bottom=float(openDriveMap.header.south)
        self.map.header.vendor=str.encode(openDriveMap.header.vendor)
    


    def setJunction(self,openDriveMap):
    
        for junction in openDriveMap.junctions.junctions.values():
            distJunction=self.map.junction.add()
            distJunction.id.id=junction.ApolloName

            distPoint=distJunction.polygon.point.add()
            p=Point(0,0,self.transformer)
            distPoint.x=p.x
            distPoint.y=p.y
            distPoint.z=0.0
            distPoint=distJunction.polygon.point.add()
            distPoint.x=p.x+5.0
            distPoint.y=p.y
            distPoint.z=0.0
            distPoint=distJunction.polygon.point.add()
            distPoint.x=p.x+5.0
            distPoint.y=p.y+5.0
            distPoint.z=0.0
            distPoint=distJunction.polygon.point.add()
            distPoint.x=p.x
            distPoint.y=p.y+5.0
            distPoint.z=0.0
            
            #self.setpolygon(dist,junction)
            for overlap_junction_lane in junction.overlap_junction_lanes:
                distOverlap=distJunction.overlap_id.add()
                distOverlap.id=overlap_junction_lane.getApolloName()
            for overlap_junction_signal in junction.overlap_junction_signals:
                distOverlap=distJunction.overlap_id.add()
                distOverlap.id=overlap_junction_signal.getApolloName()

    def setSegment(self,lane,planView,offsetsDict,segment,notes):
        curve=Curve(planView,offsetsDict,lane,self.transformer,notes)
        if notes=="central":
            lane.setCentralCurve(curve)
            lane.setCentraloffsetsDict(offsetsDict)
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

    def setLaneType(self,distLane,lane):
        if lane.type=='shoulder':
            distLane.type=distLane.LaneType.SHOULDER
        elif lane.type=='border':
            distLane.type=distLane.LaneType.SHOULDER
        elif lane.type=='driving':
            distLane.type=distLane.LaneType.CITY_DRIVING
        elif lane.type=='stop':
            log.info('translate:lane:not support lane type:stop')
        elif lane.type=='none':
            distLane.type=distLane.LaneType.NONE
        elif lane.type=='restricted':
            log.info('translate:lane:not support lane type:restricted')
        elif lane.type=='parking':
            distLane.type=distLane.LaneType.PARKING
        elif lane.type=='median':
            distLane.type=distLane.LaneType.SHOULDER
        elif lane.type=='biking':
            distLane.type=distLane.LaneType.BIKING
        elif lane.type=='sidewalk':
            distLane.type=distLane.LaneType.SIDEWALK
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
            distLane.type=distLane.LaneType.CITY_DRIVING
        else:
            log.info('translate:lane:not known lane type:'+lane.type)
        
    def setLaneFromLane(self,lane,planView,offsetsDict):
        distLane=self.map.lane.add()
        self.lanes[lane.ApolloId]=distLane
        distLane.id.id=lane.ApolloName
        if lane.forward==1:
            segment=distLane.left_boundary.curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"left")

            offsetsDict.addOffsets(lane.widthOffsets,-0.5)
            segment=distLane.central_curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"central")
            offsetsDict.popOffsets()

            offsetsDict.addOffsets(lane.widthOffsets,-1)
            segment=distLane.right_boundary.curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"right")
            offsetsDict.popOffsets()

        elif lane.forward==-1:
            segment=distLane.left_boundary.curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"left")
            #站在road方向看是right，站在lane的方向看是left

            offsetsDict.addOffsets(lane.widthOffsets,0.5)
            segment=distLane.central_curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"central")
            offsetsDict.popOffsets()

            offsetsDict.addOffsets(lane.widthOffsets,1)
            segment=distLane.right_boundary.curve.segment.add()
            self.setSegment(lane,planView,offsetsDict,segment,"right")
            offsetsDict.popOffsets()
        else:
            log.error("unknown forward")
            
        self.setLaneType(distLane,lane)
        
        if lane.speed is not None:
            distLane.speed_limit=lane.speed

        if lane.overlap_junction_lane is not None:
            distOverlap=distLane.overlap_id.add()
            distOverlap.id=lane.overlap_junction_lane.getApolloName()
        for overlap_signal_lane in lane.overlap_signal_lanes:
            distOverlap=distLane.overlap_id.add()
            distOverlap.id=overlap_signal_lane.getApolloName()

        # for overlap_crosswalk_lane in lane.overlap_crosswalk_lanes:
        #     distOverlap=dist.overlap_id.add()
        #     distOverlap.id=overlap_crosswalk_lane.getApolloName()
        #在crosswalk中处理，所以注释掉了

        if lane.type!='bidirectional':
            distLane.direction=distLane.LaneDirection.FORWARD
        else:
            distLane.direction=distLane.LaneDirection.BIDIRECTION

        for predecessor in lane.ApolloPredecessors:
            id=distLane.predecessor_id.add()
            id.id=predecessor.ApolloName
        for successor in lane.ApolloSuccessors:
            id=distLane.successor_id.add()
            id.id=successor.ApolloName
        if lane.left_neighbor_forward_lane is not None:
            id=distLane.left_neighbor_forward_lane_id.add()
            id.id=lane.left_neighbor_forward_lane.ApolloName
        if lane.left_neighbor_reverse_lane is not None:
            id=distLane.left_neighbor_reverse_lane_id.add()
            id.id=lane.left_neighbor_reverse_lane.ApolloName
        if lane.right_neighbor_reverse_lane is not None:
            id=distLane.right_neighbor_reverse_lane_id.add()
            id.id=lane.right_neighbor_reverse_lane.ApolloName
        if lane.right_neighbor_forward_lane is not None:
            id=distLane.right_neighbor_forward_lane_id.add()
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
    def setSignalReference(self,signalReference):

        distSignal=self.map.signal.add()
        distSignal.type=distSignal.Type.MIX_3_VERTICAL
        distSignal.id.id=signalReference.ApolloName
        for overlap_signal_lane in signalReference.overlap_signal_lanes:
            distOverlap=distSignal.overlap_id.add()
            distOverlap.id=overlap_signal_lane.getApolloName()
        if signalReference.overlap_junction_signal is not None:
            distOverlap=distSignal.overlap_id.add()
            distOverlap.id=signalReference.overlap_junction_signal.getApolloName()
        roadPoint=RoadPoint(signalReference.road.planView,signalReference.s,signalReference.t,self.transformer)
        
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

        
        roadPoint.Offset(-signalReference.t)
        distStopLine=distSignal.stop_line.add()
        distStopLineSegment=distStopLine.segment.add()
        if len(signalReference.validitys)!=1:
            log.warning("cannot solve it now")
        for i in range(len(signalReference.validitys[0].lane_ptrs)):
            lane=signalReference.validitys[0].lane_ptrs[i]
            width=lane.widthOffsets.getOffset(signalReference.s,"-")
            central=lane.centralOffsetsDict.getOffset(signalReference.s,"-")
            roadPoint.Offset(central)
            if i==0:
                width=lane.widthOffsets.getOffset(signalReference.s,"-")
                distStopLinePoint=distStopLineSegment.line_segment.point.add()
                roadPoint.Offset(width*0.5)
                distStopLinePoint.x=roadPoint.point.x
                distStopLinePoint.y=roadPoint.point.y
                distStopLinePoint.z=0.0
                roadPoint.Offset(-width*0.5)

            distStopLinePoint=distStopLineSegment.line_segment.point.add()
            distStopLinePoint.x=roadPoint.point.x
            distStopLinePoint.y=roadPoint.point.y
            distStopLinePoint.z=0.0

            if i==len(signalReference.validitys[0].lane_ptrs)-1:
                width=lane.widthOffsets.getOffset(signalReference.s,"-")
                distStopLinePoint=distStopLineSegment.line_segment.point.add()
                roadPoint.Offset(-width*0.5)
                distStopLinePoint.x=roadPoint.point.x
                distStopLinePoint.y=roadPoint.point.y
                distStopLinePoint.z=0.0
                roadPoint.Offset(width*0.5)
            roadPoint.Offset(-central)
        

    def setSignal(self,openDriveMap):
        for signal in openDriveMap.signals.values():
            for reference in signal.references:
                self.setSignalReference(reference)
            
    def setpolygon(self,distPolygon,polygon):
        for point in polygon.points:
            distPoint=distPolygon.point.add()
            distPoint.x=point.x
            distPoint.y=point.y
            distPoint.z=0.0

    def setObjectCrosswalk(self,object,openDriveMap):
        distCrosswalk=self.map.crosswalk.add()
        distCrosswalk.id.id=object.ApolloName
        object.setPolygon(Polygon(object,self.transformer))
        self.setpolygon(distCrosswalk.polygon,object.polygon)
        
        object.parse_junction(openDriveMap)
        if len(object.overlap_crosswalk_lanes)==0:
            log.info("cannot find overlap about crosswalk: ",object.id+" with any lane")
        for overlap_crosswalk_lane in object.overlap_crosswalk_lanes:
            distOverlap=distCrosswalk.overlap_id.add()
            distOverlap.id=overlap_crosswalk_lane.getApolloName()

            distLane=self.lanes[overlap_crosswalk_lane.lane.ApolloId]
            distOverlap=distLane.overlap_id.add()
            distOverlap.id=overlap_crosswalk_lane.getApolloName()

        
        

    def setObject(self,openDriveMap):
        for object in openDriveMap.objects:
            if object.type=='crosswalk':
                self.setObjectCrosswalk(object,openDriveMap)
    
                
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
    
    def setOverlapCrosswalkObject(self,distOverlap,crosswalk):
        distSignal=distOverlap.object.add()
        distSignal.id.id=crosswalk.ApolloName
        distSignal.crosswalk_overlap_info.CopyFrom(map_overlap_pb2.CrosswalkOverlapInfo())  #nt设计
    
    
    def setOverlap(self,openDriveMap):
        for overlap in openDriveMap.overlaps:
            if overlap.enable==False:
                continue
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

            elif overlap.kind=="crosswalk_with_lane":

                distOverlap.id.id=overlap.getApolloName()
                self.setOverlapCrosswalkObject(distOverlap,overlap.crosswalk)
                self.setOverlapLaneObject(distOverlap,overlap.lane)
            
            else:
                log.error("unknown overlap kind: "+overlap.kind)
    def parse_from_OpenDrive(self,openDriveMap):
        self.sourceCrs=pyproj.CRS.from_proj4("+proj=utm +zone=10 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
            #if proj data is empty,use "+proj=utm +zone={} +ellps=WGS84" by default
        self.distCrs=pyproj.CRS.from_proj4("+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
       
        self.setHeader(openDriveMap)
        self.setJunction(openDriveMap)
        self.setLane(openDriveMap)
        self.setRoad(openDriveMap)
        self.setSignal(openDriveMap)
        self.setObject(openDriveMap)
        self.setOverlap(openDriveMap)
	