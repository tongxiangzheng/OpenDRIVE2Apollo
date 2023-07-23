from collections import defaultdict

def dfs(now,len):
	for i in range(len):
		print(' ',end='')
	print("type=",now.nodeType,"name=",now.nodeName,",value=",now.nodeValue)
	for child in now.childNodes:
		dfs(child,len+1)
                
def defaultNone():
    return []

def sub2dict(node):
    subDict=defaultdict(defaultNone)
    nodelist=node.childNodes
    for subnode in nodelist:
        name=subnode.nodeName
        subDict[name].append(subnode)
    return subDict
