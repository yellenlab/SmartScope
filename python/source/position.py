
'''
This file impliments the PositionList, StagePosition, 
and MultiStagePosition types as used in micro-manager 
beanshell. 

TODO:
    - Add PositionList JSON serialize funtion
    - Add PositionList save/load from file 
'''
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


class PositionList:
    def __init__(self, msp=None):
        self.positions = []
        if msp is not None and isinstance(msp, MultiStagePosition):
            self.addPosition(msp)

    def addPosition(self, pos=None, idx=None):
        if idx is None and pos is not None:
            self.positions.append(pos)
        elif idx is not None and pos:
            self.positions.insert(idx, pos)
        else:
            return False

    def getPositionIndex(self, label):
        for idx, p in enumerate(self.positions):
            if p.label == label:
                return idx
        return False
    
    def relacePosition(self, idx, pos):
        assert self.isLabelUnique(pos.label),  True
        if idx > 0 and idx < len(self.positions):
            self.positions[idx] = pos
    
    def getNumberOfPositions(self):
        return len(self.positions)

    def clearAllPositions(self):
        self.positions.clear()
    
    def removePosition(self, idx):
        self.positions.pop(idx)

    def isLabelUnique(self, label):
        for pos in self.positions:
            if pos.label == label:
                return False
        return True
    
    def getPosition_xyz(self, idx):
        return self.positions[idx].get(index=0).x, self.positions[idx].get(index=0).y, self.positions[idx].get(index=1).z

    def visualize(self):
        fig = plt.figure()
        plot = fig.add_subplot(111,projection='3d')

        xpos = []
        ypos = []
        zpos = []

        xyStage = self.positions[0].defaultXYStage
        zStage = self.positions[0].defaultZStage

        for i in range(self.getNumberOfPositions()):
            xpos.append(self.positions[i].get(stageName=xyStage).x)
            ypos.append(self.positions[i].get(stageName=xyStage).y)
            zpos.append(self.positions[i].get(stageName=zStage).z)
        
        plot.scatter(xpos,ypos,zpos)
        plot.set_xlabel('X')
        plot.set_ylabel('Y')
        plot.set_zlabel('Z')


class StagePosition:
    def __init__(self):
        self.stageName = 'Undefined'
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.numAxes = 1
    
    def equals(self, pos):
        if not isinstance(pos, StagePosition):
            return False
        return (self.x == pos.x and
                self.y == pos.y and
                self.z == pos.z and
                self.numAxes == pos.numAxes and
                self.stageName == pos.stageName)
    
    def getVerbose(self):
        if self.numAxes == 1:
            return self.stageName + "(" + str(self.x) + ")"
        elif self.numAxes == 2:
            return self.stageName + "(" + str(self.x) + "," + str(self.y) + ")"
        else:
            return self.stageName + "(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"


class MultiStagePosition:
    def __init__(self, xyStage=None,
                       x=None,
                       y=None, 
                       zStage=None,
                       z=None):
        
        self.stagePosList = []
        self.label = 'Undefined'
        self.defaultZStage = ''
        self.defaultXYStage = ''
        self.gridRow = 0
        self.gridCol = 0
        self.properties = {}

        if (xyStage is not None and 
                  x is not None and 
                  y is not None and 
                  zStage is not None and 
                  z is not None):
            xyPos = StagePosition()
            xyPos.stageName = 'xyStage'
            xyPos.numAxes = 2
            xyPos.x = x
            xyPos.y = y
            self.defaultXYStage = 'xyStage'
            self.add(xyPos)

            zPos = StagePosition()
            zPos.stageName = 'zStage'
            zPos.numAxes = 1
            zPos.z = z
            self.defaultZStage = 'zStage'
            self.add(zPos)
    
    def add(self, sp):
        self.stagePosList.append(sp)

    def remove(self, sp):
        self.stagePosList.remove(sp)

    def size(self):
        return len(self.stagePosList)
    
    def get(self, index=None, stageName=None, ):
        if index is not None:
            try:
                return self.stagePosList[index]
            except Exception as e:
                print(e)
        elif stageName is not None:
            for sp in self.stagePosList:
                if sp.stageName == stageName:
                    return sp
            return False
        return False
    
    def hasProperty(self, key):
        return key in self.properties
    
    def getProperty(self, key):
        if key in self.properties:
            return self.properties[key]
        else:
            return False
    
    def equals(self, msp):
        if not isinstance(msp, MultiStagePosition):
            return False
        
        if not (self.label == msp.label and
                self.defaultXYStage == msp.defaultXYStage and
                self.defaultZStage == msp.defaultZStage and
                self.gridRow == msp.gridRow and 
                self.gridCol == msp.gridCol and
                len(self.stagePosList) == len(msp.stagePosList)):
            return False

        for i in range(self.size()):
            if not self.get(index=i) == msp.get(index=i):
                return False
        
        for key in self.properties.items():
            if not self.properties[key] == msp.properties[key]:
                return False

        if not len(self.properties) == len(msp.properties):
            return False

        return True 
    
    def print_msp(self):
        print('X = ', self.stagePosList[0].x)
        print('Y = ', self.stagePosList[0].y)
        print('Z = ', self.stagePosList[1].z)
   
