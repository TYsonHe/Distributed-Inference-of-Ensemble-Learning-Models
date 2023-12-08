'''
Author: yingxin wang
Date: 2023-11-21 17:10:20
LastEditors: yingxin wang
LastEditTime: 2023-11-22 17:01:00
Description: 请求发射器
'''

import requests
import pandas as pd
import time
import random
import matplotlib.pyplot as plt
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

class RequestEmitter:
    def __init__(self):
        self.stats = {
            'batch_all_requests_nums': [], # 每批次请求数
            'batch_success_requests_nums': [], # 每批次成功请求数
            'batch_all_responses': [] # 每批次请求结果
        }

    def initHttpRequest(self,url,type,success_code=200,headers={'Content-Type': 'text/plain'}):
        self.url = url
        self.type = type
        self.success_code = success_code
        self.headers = headers

    def initData(self,is_single_data=True,has_test=True,train_file_path=None,test_file_path=None):
        self.is_single_data = is_single_data
        self.has_test = has_test

        df = pd.read_csv(train_file_path, header=None)
        # 将每一行的数据连接成逗号分隔的字符串
        processed_data = df.apply(lambda row: ','.join(map(str, row)), axis=1)
        self.x=processed_data.tolist()

        if has_test:
            with open(test_file_path,"r") as f:
                data = f.read()
            self.y=data

    def _makeRequest(self,data):
        try:
            if self.type == "GET":
                response = requests.get(self.url,data=data,headers=self.headers)
            elif self.type == "POST":
                response = requests.post(self.url,data=data,headers=self.headers)
            else:
                print("Error: type should be one of GET, POST")
                return None
            print(f"Request finished with status code: {response.status_code}")
            return response
            # 如果有其他需要处理的信息，可以在这里添加相应的逻辑
        except Exception as e:
            print(f"Error making request to {self.url}: {str(e)}")
            return None

    def loadTest(self, request_interval, random_range, batch_nums):
        # 压测函数，request_interval为请求间隔（秒），random_range为随机数范围，batch_nums为批次数
        # random_range为随机数范围，是一个元组，如(1, 10)
        
        sent_batch_nums = 0
        sent_data_nums = 0
        while sent_batch_nums < batch_nums:
            # 随机一个当前批次请求数
            current_num_requests = random.randint(random_range[0], random_range[1])
            print(f"Sending {current_num_requests} requests")
            # 记录每批次的请求数
            self.stats['batch_all_requests_nums'].append(current_num_requests)
            # 记录每批次的请求结果
            batch_responses = []
            batch_success_requests_num=0

            # 使用ThreadPoolExecutor实现并发请求
            with ThreadPoolExecutor(max_workers=current_num_requests) as executor:
                # 循环提交请求
                future_to_data = {executor.submit(self._makeRequest, self.x[sent_data_nums]): self.x[sent_data_nums] for _ in range(current_num_requests)}
                
                for future in concurrent.futures.as_completed(future_to_data):
                    data = future_to_data[future]
                    try:
                        response = future.result()
                        # 记录请求结果
                        print(f"Request finished with status code: {response.status_code}")
                        batch_responses.append(response)
                        # 记录成功请求数
                        if response.status_code == self.success_code:
                            batch_success_requests_num += 1
                    except Exception as e:
                        print(f"An error occurred: {str(e)}")

                    sent_data_nums += 1
            
            self.stats['batch_all_responses'].append(batch_responses)
            self.stats['batch_success_requests_nums'].append(batch_success_requests_num)
            sent_batch_nums += 1
            # 间隔指定时间
            time.sleep(request_interval)

    def plotGraph(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.stats['batch_all_requests_nums'], label='Batch All Requests')
        plt.plot(self.stats['batch_success_requests_nums'], label='Batch Successful Requests', linestyle='dashed', marker='o')
        plt.xlabel('Batch Number')
        plt.ylabel('Number of Requests')
        plt.title('Number of Requests Over Batches')
        plt.legend()
        plt.show()


# request_emitter = RequestEmitter()
# request_emitter.initHttpRequest('http://10.60.150.177:31112/function/stock-predict', 'GET')
# request_emitter.initData(False, False, 'testDataSets/stockPredict/dji_x_test_full.csv')
# # %%
# request_emitter.loadTest(1, (1, 9), 4)
# # %%
# request_emitter.plotGraph()