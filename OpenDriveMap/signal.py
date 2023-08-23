from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,Counter

class Overlap_signal_lane:
    def __init__(self,signal,lane):
        self.kind="signal_with_lane"
        signal.overlap_signal_lanes.append(self)
        lane.overlap_signal_lanes.append(self)
        self.signal=signal
        self.lane=lane
    def getApolloName(self):
        ApolloName='overlap_signal_'+self.signal.ApolloId+'_lane_'+self.lane.ApolloId
        return ApolloName
    
class Overlap_junction_signal:
    def __init__(self,junction,signal):
        self.kind="junction_with_signal"
        signal.overlap_junction_signal=self
        junction.overlap_junction_signals.append(self)
        self.junction=junction
        self.signal=signal
    def getApolloName(self):
        ApolloName='overlap_junction_I0_J'+self.junction.ApolloId+'_0_'+self.signal.ApolloId
        return ApolloName

class Validity:
    def __init__(self,node):
        self.fromLane=node.getAttribute('fromLane')
        self.toLane=node.getAttribute('toLane')
        self.lanes=[]
        for i in range(int(self.fromLane),int(self.toLane)+1):
            if i==0:
                continue
            self.lanes.append(str(i))
        self.lane_ptrs=[]
        self.fromLane_ptr=None
        self.toLane_ptr=None
    def addReference(self,validity):
        self.self.references.append(validity)
    def parse(self,signalReference,map):
        referenceRoad=signalReference.road
        for lane in self.lanes:
            self.lane_ptrs.append(referenceRoad.getLaneById(lane,'start'))
        
class Siginal:
    def __init__(self,node,road):
        self.id=node.getAttribute('id')
        self.name=node.getAttribute('name')
        self.dynamic=node.getAttribute('dynamic')
        self.road=road
        self.junction=None
        subDict=sub2dict(node)
        self.validitys=[]
        self.referenceValiditys=[]
        self.overlap_signal_lanes=[]
        self.overlap_junction_signal=None

        validityList=subDict['validity']
        for validity in validityList:
            self.validitys.append(Validity(validity))
        self.road=road
    def addValidity(self,validity):
        self.referenceValiditys.append(validity)

    def parse(self,map,signalCounter):
        self.ApolloId=signalCounter.getId()
        self.ApolloName="signal_"+self.ApolloId
        for validity in self.validitys:
            validity.parse(self,map)
            for lane in validity.lane_ptrs:
                map.addOverlap(Overlap_signal_lane(self,lane))
        

class SignalReference:
    def __init__(self,node,road):
        self.id=node.getAttribute('id')
        self.s=node.getAttribute('s')
        self.t=node.getAttribute('t')
        subDict=sub2dict(node)
        self.validitys=[]
        validityList=subDict['validity']
        for validity in validityList:
            self.validitys.append(Validity(validity))
        self.road=road
        
    def parse(self,map):
        signal=map.signals[self.id]
        for validity in self.validitys:
            validity.parse(self,map)
            signal.addValidity(validity)
            for lane in validity.lane_ptrs:
                map.addOverlap(Overlap_signal_lane(signal,lane))
        if signal.junction is None:
            signal.junction=self.road.junction
            map.addOverlap(Overlap_junction_signal(self.road.junction,lane))
        elif signal.junction!=self.road.junction:
            log.warning("one signal have more than one junction: "+signal.junction.id+" and "+self.road.junction.id)
        
class Signals:
    def __init__(self,node,road,map):
        self.siginals=[]
        self.signalReferences=[]
        siginals=node.getElementsByTagName('signal')
        #print(siginals)
        for siginal in siginals:
            sig=Siginal(siginal,road)
            self.siginals.append(sig)
            map.signals[sig.id]=sig
        
        signalReferences=node.getElementsByTagName('signalReference')
        for signalReference in signalReferences:
            self.signalReferences.append(SignalReference(signalReference,road))
            
    def parse(self,map,signalCounter):
        for signalReference in self.signalReferences:
            signalReference.parse(map)
            
            
        for siginal in self.siginals:
            siginal.parse(map,signalCounter)
        

        