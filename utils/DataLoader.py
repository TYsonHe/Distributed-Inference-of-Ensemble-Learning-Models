import pandas as pd
import numpy as np
import random


class DataLoader:
    '''
    数据加载类
    '''

    def __init__(self, xPath: str, yPath: str) -> None:
        self.xPath = xPath
        self.yPath = yPath

    def loadX(self) -> list:
        '''
        加载X
        '''
        inputDatas = pd.read_csv(self.xPath)
        inputDatas = np.array(inputDatas)
        inputDatas = inputDatas.tolist()
        self.inputDatas_str = [','.join(map(str, row)) for row in inputDatas]
        return self.inputDatas_str

    def loadY(self) -> list:
        '''
        加载Y
        '''
        yLabels = pd.read_csv(self.yPath)
        yLabels = np.array(yLabels)
        yLabels = yLabels.tolist()
        self.yLabels = [float(i[0]) for i in yLabels]
        return self.yLabels

    def shuffle(self):
        '''
        打乱数据要保证X和Y的对应关系
        但不改变self.inputDatas_str和self.yLabels的值(保持原来的顺序不变)
        '''
        data = list(zip(self.inputDatas_str, self.yLabels))
        random.shuffle(data)
        shuffledInputDatas_str, shuffledYLabels = zip(*data)
        return shuffledInputDatas_str, shuffledYLabels

    def showPaths(self):
        '''
        显示路径
        '''
        print("X的路径为:", self.xPath)
        print("Y的路径为:", self.yPath)

    def showDatas(self):
        '''
        显示数据
        '''
        print("X的数据为:", self.inputDatas_str)
        print("Y的数据为:", self.yLabels)
    pass
