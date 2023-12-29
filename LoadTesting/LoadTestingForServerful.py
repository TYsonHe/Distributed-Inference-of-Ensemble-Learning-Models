import datetime
import pandas as pd
import math
import random
import time

from locust import LoadTestShape, task,  constant, HttpUser

data_path="D:/CodingWork/git/Distributed-Inference-of-Ensemble-Learning-Models/testDataSets/stockPredict/dji_x_test_full.csv"
df = pd.read_csv(data_path, header=None)
processed_data = df.apply(lambda row: ','.join(map(str, row)), axis=1)
datas=processed_data.tolist()
datas_length = len(datas)

invoke_data_path="invoke_data2.csv"
invoke_data = pd.read_csv(invoke_data_path, header=None)
invoke_data_length = len(invoke_data)

#所有的时间单位都是秒
pressure_test_interval=6   #每两个并发的间隔时间
single_test_duration=150   #一批次压测时间
single_stop_duration=15    #一批次停止压测时间
max_request_time=20        #预估一个请求的最大时间,用于限制压测的执行时长

class MyUser(HttpUser):
    host = "http://10.60.150.177:32056"  # 设置主机地址

    @task(1)
    def task_1(self):
        start_time = time.time()

        global datas_length,datas
        random_number = random.randint(0, datas_length-1)
        data=datas[random_number]
        response = self.client.post('/',data=data)
        print(f"Response status code: {response.status_code}")
        time_delay = time.time() - start_time

        if time_delay > pressure_test_interval:
            pass
        else:
            wait_time = pressure_test_interval - time_delay
            time.sleep(wait_time)

class MyCustomShape(LoadTestShape):
    '''
        spawn_rate -- 用户在每一步的停止/启动的多少用户数
        time_limit -- 时间限制压测的执行时长
    '''
    time_limit = invoke_data_length*(max_request_time+single_stop_duration) #压测的执行时长,这个随便设的,得足够大
    spawn_rate = 100
    
    def tick(self):
        run_time = self.get_run_time()

        #需要看当前时间是否在压测的时间段内
        is_in_test_duration = (run_time % (single_test_duration+single_stop_duration)) < single_test_duration
        
        if run_time < self.time_limit and is_in_test_duration:
            index = (int(run_time/pressure_test_interval)+1)

            if index >= invoke_data_length: #如果超过了数据的长度,就停止压测
                return None
            
            user_count = int(invoke_data.at[index,0])
            return (user_count, self.spawn_rate)
        elif run_time < self.time_limit and not is_in_test_duration:
            return (0, self.spawn_rate)

        return None


