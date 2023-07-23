from loguru import logger as log
from OpenDriveMap.dom_tool import sub2dict,dfs

class GeoReference:									#地理坐标参考
    def __init__(self,node):
        self.data=node.firstChild.nodeValue
        #没想好怎么处理这个数据
		#data的样例: +proj=tmerc +lat_0=0 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +geoidgrids=egm96_15.gtx +vunits=m +no_defs

class Header:
    def __init__(self,node):
        subDict=sub2dict(node)
        self.revMajor=node.getAttribute('revMajor')	#主版本号
        self.revMinor=node.getAttribute('revMinor')	#次版本号
        self.name=node.getAttribute('name')			#数据库名称
        self.version=node.getAttribute('version')	#本路网的版本号
        self.date=node.getAttribute('date')			#创建时间
        self.north=node.getAttribute('north')		#最大惯性y值
        self.south=node.getAttribute('south')		#最小惯性y值
        self.east=node.getAttribute('east')			#最大惯性x值
        self.west=node.getAttribute('west')			#最小惯性x值
        self.vendor=node.getAttribute('vendor')		#开发商名称
        

        self.geoReference=GeoReference(subDict['geoReference'][0])
        #userData先不管了
        