import threading
import time

import requests
import yaml


class EnsembleModel:
    '''
    集成模型类
    需要传入url字典的列表
    功能:
    1.输出并各个模型的预测结果,时间开销(单位:秒)
    2.输出并返回集成模型的预测结果
    urlDict:
        modelName:模型名字
        modelUrl:模型的url
    results:
        results是一个列表,列表中的每个元素是一个字典,字典中有两个键值对:
        modelName:模型名字
        predictValue:模型的预测结果
    '''

    def __init__(self, modelConfigPath: str) -> None:
        '''
        初始化
        关于urlDict:
            key:模型名字
            value:模型的url
        '''
        self.modelConfigPath = modelConfigPath
        self.loadModelConfig()
        self.results = []

    def loadModelConfig(self) -> None:
        '''
        从modelConfigPath中读取模型配置
        modelConfig:
            yaml格式的文件
        '''
        with open(self.modelConfigPath, 'r') as f:
            modelConfig = yaml.load(f, Loader=yaml.FullLoader)
        self.urlDictList = modelConfig['urlDictList']

    def addModel(self, urlDict) -> None:
        '''
        添加模型的url
        '''
        self.urlDictList.append(urlDict)

    def deleteModel(self, urlDict) -> None:
        '''
        删除模型的url
        '''
        self.urlDictList.remove(urlDict)

    def showCurrentModels(self) -> None:
        '''
        显示当前的模型
        '''
        print("当前的模型有:")
        for urlDict in self.urlDictList:
            print(urlDict['modelName'])

    def getModelsNum(self) -> int:
        '''
        获取当前模型的数量
        '''
        return len(self.urlDictList)

    def getUrlDictList(self) -> list:
        '''
        获取当前模型的url字典列表
        '''
        return self.urlDictList

    def sendRequestAndStoreResult(self, urlDict, data, printResult=False):
        '''
        发送请求并将结果存储在results列表中
        时间单位:秒
        '''
        startTime = time.time()  # 记录开始时间
        url = urlDict['modelUrl']
        if printResult:
            print(time.asctime(), "Sending request to", url)
        r = requests.get(url, data=data)
        endTime = time.time()  # 记录结束时间
        modelResult = dict()
        modelResult['modelName'] = urlDict['modelName']
        modelResult['predictValue'] = r.text.replace('\n', '')
        modelResult['timeTaken'] = endTime - startTime
        self.results.append(modelResult)
        if printResult:
            print("Time taken for", url, ":",
                  modelResult['timeTaken'], "seconds")  # 计算执行时间并打印

    def run(self, inputData: str, printResult=False) -> tuple:
        '''
        运行集成模型
        输入:
            inputData,字符串,模型的输入数据
            printResult,布尔值,是否打印结果
        返回值:
        ensemblePredictValue:
            集成模型的预测结果
        results:
            results是一个列表,列表中的每个元素是一个字典,字典中有两个键值对:
            modelName:模型名字
            predictValue:模型的预测结果
        '''
        # 清空results
        self.results = []
        # 创建线程列表
        modelNum = len(self.urlDictList)
        threads = []
        # 创建线程
        for i in range(modelNum):
            thread = threading.Thread(
                target=self.sendRequestAndStoreResult, args=(self.urlDictList[i], inputData, printResult))
            threads.append(thread)
        # 启动线程
        for i in range(modelNum):
            threads[i].start()
        # 等待线程执行完毕
        for i in range(modelNum):
            threads[i].join()
        # 打印并返回结果
        if printResult:
            print("Result:")
            for i in range(modelNum):
                print(self.results[i]['modelName'],
                      ":", self.results[i]['predictValue'])
        ensemblePredictValue = 0
        for i in range(modelNum):
            ensemblePredictValue += float(self.results[i]['predictValue'])
        ensemblePredictValue /= modelNum
        if printResult:
            print("集成模型预测结果:", ensemblePredictValue)
        return self.results, ensemblePredictValue


# 测试代码
if __name__ == '__main__':
    inputData = '0.0,0.676964737573449,1.5622877677766447,0.5555330632092685,0.4579332723844055,0.5947720595105965,-0.18367590319728047,-0.41592761460465344,-0.39791121287711007,-0.40996003084539434,-0.3979112128771097,2.3704530408864093,-0.40395533950919793,-0.40996003084539434'
    ensembleModel = EnsembleModel('configs/models.yml')
    singleResult = ensembleModel.run(inputData)
    print(singleResult)
