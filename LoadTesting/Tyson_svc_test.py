import pandas as pd
import random
import json

from locust import LoadTestShape, task, constant, HttpUser

# data_path = "D:/CodingWork/git/Distributed-Inference-of-Ensemble-Learning-Models/testDataSets/stockPredict/dji_x_test_full.csv"
data_path = "../testDataSets/X_test.csv"
df = pd.read_csv(data_path, header=None)
# 去掉第一行的列名
df = df.drop([0])
processed_data = df.apply(lambda row: ','.join(map(str, row)), axis=1)
datas = processed_data.tolist()
print(datas)
datas_length = len(datas)

y_data_path = "../testDataSets/y_test.csv"
y_df = pd.read_csv(y_data_path, header=None)
# 去掉第一行的列名
y_df = y_df.drop([0])
y_processed_data = y_df.apply(lambda row: ','.join(map(str, row)), axis=1)
y_datas = y_processed_data.tolist()
print(y_datas)
y_datas_length = len(y_datas)

invoke_data_path = "invoke_data.csv"
invoke_data = pd.read_csv(invoke_data_path, header=None)
invoke_data_length = len(invoke_data)


class MyUser(HttpUser):
    wait_time = constant(1)
    host = "http://10.60.150.177:32005"  # 设置主机地址

    def on_start(self):
        self.headers = {
            "Content-Type": "application/json"
        }

    @task(1)
    def task_1(self):
        global datas_length, datas, y_datas_length, y_datas
        random_number = random.randint(0, datas_length - 1)
        data = json.dumps({
            "input_str": datas[random_number],
            "y_true": y_datas[random_number]
        })
        response = self.client.post('/', headers=self.headers, data=data)
        print(f"Response status code: {response.status_code}")


class MyCustomShape(LoadTestShape):
    '''
        spawn_rate -- 用户在每一步的停止/启动的多少用户数
        time_limit -- 时间限制压测的执行时长
    '''
    time_limit = 1440 * 20
    spawn_rate = 100

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.time_limit:
            global invoke_data_length, invoke_data
            index = int((int(run_time / 3) + 1) % invoke_data_length)
            user_count = int(invoke_data.at[index, 0])
            if user_count > 10:
                user_count = user_count // 10
            return (user_count, self.spawn_rate)
        return None
