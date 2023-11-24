import random
import threading
import time

import requests
import socket
import yaml
import re


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
        self.x_call_ids = []
        self.x_call_nums = len(self.urlDictList)

    def loadModelConfig(self) -> None:
        '''
        从modelConfigPath中读取模型配置
        modelConfig:
            yaml格式的文件
        '''
        with open(self.modelConfigPath, 'r') as f:
            modelConfig = yaml.load(f, Loader=yaml.FullLoader)
        self.urlDictList = modelConfig['urlDictList']
        self.callback_url = modelConfig['callback_url']
        # 分发权重
        self.distributeWeights()

    def distributeWeights(self) -> None:
        '''
        集成模型的参数分发
        '''
        num_models = self.getModelsNum()
        # 随机生成权重
        self.weights = [random.uniform(0, 1) for _ in range(num_models)]
        # 归一化
        self.weights = [w / sum(self.weights) for w in self.weights]
        # 分发权重
        for urlDict, weight in zip(self.urlDictList, self.weights):
            urlDict['weight'] = weight

    def get_weight(self, model_id: int) -> float:
        '''
        获取模型的权重
        '''
        for urlDict in self.urlDictList:
            if urlDict['model_id'] == model_id:
                return urlDict['weight']

    def modify_weight(self, model_id: int, new_weight: float) -> None:
        '''
        修改模型的权重
        '''
        for urlDict in self.urlDictList:
            if urlDict['model_id'] == model_id:
                urlDict['weight'] = new_weight

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

    def getModelName(self, index) -> str:
        '''
        获取当前模型的名字
        '''
        return self.urlDictList[index]['modelName']

    def get_model_id(self, model_name: str) -> int:
        '''
        获取模型的id
        '''
        for urlDict in self.urlDictList:
            if urlDict['modelName'] == model_name:
                return urlDict['model_id']

    # 只需要请求体
    def extract_request_body(self, http_request_str: str):
        # 寻找空行分隔请求头和请求体
        double_newline_index = http_request_str.find('\r\n\r\n')

        if double_newline_index != -1:
            # 提取请求体
            request_body = http_request_str[double_newline_index + 4:]
            return request_body

        return None

    def send_request(self, urlDict, data, printResult=False):
        '''
        发送请求并将结果一部分存储在results列表中
        时间单位:秒
        '''
        startTime = time.time()  # 记录开始时间
        url = urlDict['modelUrl']
        if printResult:
            print(time.asctime(), "Sending request to", url)
        headers = {'X-Callback-Url': self.callback_url}
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 202:
            endTime = time.time()  # 记录结束时间
            # 提取并保存X-Call-Id
            x_call_id = response.headers.get('X-Call-Id')
            if x_call_id:
                self.x_call_ids.append(x_call_id)
            modelResult = dict()
            modelResult['modelName'] = urlDict['modelName']
            modelResult['x_call_id'] = x_call_id
            modelResult['startTime'] = startTime
            modelResult['endTime'] = endTime
            modelResult['timeTaken'] = endTime - startTime
            modelResult['weight'] = urlDict['weight']
            # 提取并保存预测结果
            self.results.append(modelResult)

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
                target=self.send_request, args=(self.urlDictList[i], inputData, printResult))
            threads.append(thread)
        # 启动线程
        for i in range(modelNum):
            threads[i].start()
        # 等待线程执行完毕
        for i in range(modelNum):
            threads[i].join()

        # 等待回调
        print("Waiting for callback...")
        print(self.x_call_ids)

        ##开始监听端口获取回调结果
        # 启动HTTP服务器
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 启用 SO_REUSEPORT 选项，保证多个进程可以同时监听一个端口
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        server_socket.bind(('0.0.0.0', 8888))
        server_socket.listen(1)
        print("Server listening on port 8888")

        while True:
            # 等待客户端连接
            client_socket, addr = server_socket.accept()
            print("Connection from {addr}")
            # 接收数据
            data = client_socket.recv(1024)
            if not data:
                break

            # data本身是byte型
            data = str(data, 'utf-8')
            # 使用正则表达式提取X-Call-Id
            match = re.search(r'X-Call-Id: (.+)', data)

            if match:
                x_call_id = match.group(1)
                x_call_id = x_call_id.replace("\r", "").replace("\n", "")

                # 如果提取到的X-Call-Id在数组中，进行相应的处理
                if x_call_id in self.x_call_ids:
                    results_str = self.extract_request_body(data)
                    # 在results中找到对应的模型
                    for i in range(modelNum):
                        if self.results[i]['x_call_id'] == x_call_id:
                            self.results[i]['predictValue'] = results_str
                    self.x_call_nums = self.x_call_nums - 1

                    # 获取到所有的内容
                    if self.x_call_nums == 0:
                        client_socket.close()
                        break

            # 关闭连接
            client_socket.close()

        # 关闭服务器socket
        server_socket.close()
        ##结束监听端口获取回调结果

        # 打印并返回结果
        if printResult:
            print("Result:")
            for i in range(modelNum):
                print(self.results[i]['modelName'],
                      ":", self.results[i]['predictValue'])
        ensemblePredictValue = 0
        for i in range(modelNum):
            ensemblePredictValue += float(
                self.results[i]['predictValue']) * self.results[i]['weight']
        if printResult:
            print("集成模型预测结果:", ensemblePredictValue)
        return self.results, ensemblePredictValue


# 测试代码
if __name__ == '__main__':
    inputData = '0.0,0.676964737573449,1.5622877677766447,0.5555330632092685,0.4579332723844055,0.5947720595105965,-0.18367590319728047,-0.41592761460465344,-0.39791121287711007,-0.40996003084539434,-0.3979112128771097,2.3704530408864093,-0.40395533950919793,-0.40996003084539434'
    ensembleModel = EnsembleModel('configs/models.yml')
    singleResult = ensembleModel.run(inputData)
    print(singleResult)
