from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,Counter

class Validity:
    def __init__(self,node):
        self.fromLane=node.getAttribute('fromLane')
        self.toLane=node.getAttribute('toLane')
        
class Siginal:
    def __init__(self,node):
        self.id=node.getAttribute('id')
        self.name=node.getAttribute('name')
        self.dynamic=node.getAttribute('dynamic')
        subDict=sub2dict(node)
        validityList=subDict['validity']
        for validity in validityList:
            self.validitys.append(Validity(validity))
    def parse(self,map):
        "continue"

class SignalReference:
    def __init__(self,signalReferences):
        "continue"
    def toSignal(self,map):
        "continue"
        
class Signals:
    def __init__(self,node,map):
        self.siginals=[]
        self.signalReferences=[]
        siginals=node.getElementsByTagName('siginal')
        for siginal in siginals:
            sig=Siginal(siginal)
            self.siginals.append(sig)
            map.signals[sig.id]=sig
        
        signalReferences=node.getElementsByTagName('signalReference')
        for signalReference in signalReferences:
            self.signalReferences.append(SignalReference(signalReference))
            
    def parse(self):
        for signalReference in self.signalReferences:
            self.siginals.append(signalReference.toSignal(map))
            
        for siginal in self.siginals:
            siginal.parse(map)
        

        