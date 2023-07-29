from math import sqrt
class Point:
    def __init__(self,s,x,y):
        self.s=s
        self.x=x
        self.y=y
        self.preLine=None
        self.sucLine=None
class Line:
    def __init__(self,prePoint,sucPoint):
        self.prePoint=prePoint
        prePoint.sucLine=self
        self.sucPoint=sucPoint
        sucPoint.preLine=self
        self.calcLength()
    def calcLength(self):
        self.length=sqrt((self.prePoint.x-self.sucPoint.x)**2+(self.prePoint.y-self.sucPoint.y)**2)

class Curve:
    def __init__(self,PlanView):
        "continue"