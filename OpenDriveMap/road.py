from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs


class Link:
    def __init__(self,node):
        #print(node)
        self.kind=node.getElementsByTagName('name')
        self.elementType=node.getAttribute('elementType')
        if self.elementType=='road':
            self.elementId=node.getAttribute('elementId')
            self.contactPoint=node.getAttribute('contactPoint')
        elif self.elementType=='junction':
            self.elementType=node.getAttribute('elementType')
        else:
            log.warning("unknown link type")

class Speed:
    def __init__(self,node):
        self.max=node.getAttribute('max')
        self.unit=node.getAttribute('unit')
        
class Type:
    def __init__(self,node):
        self.type=node.getAttribute('type')
        self.speed=Speed(node.getElementsByTagName('speed')[0])
        
    
class Geometry:
    def __init__(self,node):
        #dfs(node,1)
        self.s=node.getAttribute('s')
        self.x=node.getAttribute('x')
        self.y=node.getAttribute('y')
        self.hdg=node.getAttribute('hdg')
        self.length=node.getAttribute('length')
        self.type="unknown"
        if len(node.getElementsByTagName('line'))==1:
            self.type="line"
        elif len(node.getElementsByTagName('spiral'))==1:
            self.type="spiral"
            log.warning("Geometry:not support spiral")
            #暂不支持螺旋线
        elif len(node.getElementsByTagName('arc'))==1:
            self.type="arc"
            self.curvature=node.getElementsByTagName('arc')[0].getAttribute('curvature')
            #log.debug("Geometry:arc curvature is "+self.curvature)

        else:
            log.warning("Geometry:unknown geometry type")


class PlanView:
    def __init__(self,node):
        self.geometrys=[]
        nodelist=node.getElementsByTagName('geometry')
        for node in nodelist:
            self.geometrys.append(Geometry(node))
    


class Road:
    def __init__(self,node):
        self.name=node.getAttribute('name')
        self.length=node.getAttribute('length')
        self.id=node.getAttribute('id')
        self.junction=node.getAttribute('junction')
        #self.rule="RHT" 默认靠右行驶

        subDict=sub2dict(node)
        #log.debug("road id: "+self.id)

        #link
        linkList=subDict['link']
        for links in linkList:
            if len(links.getElementsByTagName('predecessor'))>2:
                log.warning("road:predecessor too much")
            if len(links.getElementsByTagName('successor'))>2:
                log.warning("road:successor too much")
            
            for l in links.getElementsByTagName('predecessor'):
                self.predecessor=Link(l)
            for l in links.getElementsByTagName('successor'):
                self.successor=Link(l)
        
        #type
        typeList=subDict['type']
        if len(typeList) == 1:
            self.type=Type(typeList[0])
        else:
            log.info("road id "+self.id+" : have no type or too much types")


        planViewList=subDict['planView']
        self.planView=PlanView(planViewList[0])


class Roads:
    def __init__(self,nodeList):
        self.roads=dict()
        for node in nodeList:
            id=node.getAttribute('id')
            #print(id)
            self.roads[id]=Road(node)