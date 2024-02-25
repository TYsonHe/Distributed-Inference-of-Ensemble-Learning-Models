import pandas as pd
import random
import json
import pendulum

from locust import LoadTestShape, task, constant, HttpUser
from utils.CrudDb import CrudDb

db = CrudDb('../configs/db.yml')
TIME_ZONE = 'UTC'
# data_path="D:/CodingWork/git/Distributed-Inference-of-Ensemble-Learning-Models/testDataSets/stockPredict/dji_x_test_full.csv"
data_path = "../testDataSets/X_test.csv"

df = pd.read_csv(data_path, header=None)
# 去掉第一行的列名
df = df.drop([0])
processed_data = df.apply(lambda row: ','.join(map(str, row)), axis=1)
datas = processed_data.tolist()
# print(datas)
datas_length = len(datas)

y_data_path = "../testDataSets/y_test.csv"
y_df = pd.read_csv(y_data_path, header=None)
# 去掉第一行的列名
y_df = y_df.drop([0])
y_processed_data = y_df.apply(lambda row: ','.join(map(str, row)), axis=1)
y_datas = y_processed_data.tolist()
# print(y_datas)
y_datas_length = len(y_datas)

invoke_data_path = "invoke_data2.csv"
invoke_data = pd.read_csv(invoke_data_path, header=None)
invoke_data_length = len(invoke_data)

# 所有的时间单位都是秒
pressure_test_interval = 3  # 每两个并发的间隔时间
single_test_duration = 60  # 一批次压测时间
single_stop_duration = 30  # 一批次停止压测时间
max_request_time = 20  # 预估一个请求的最大时间,用于限制压测的执行时长


class MyUser(HttpUser):
    wait_time = constant(1)
    host = "http://10.60.150.177:32361"  # 设置主机地址

    def on_start(self):
        self.headers = {
            "Host": "em-fn.knative-fn.knative.example.com",
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
        # print(f"Response status code: {response.status_code}")

    # def on_stop(self):
    #     pass
    #     # super().on_stop()
    #     # end_time = time.time()  # 记录压测结束时间
    #     # elapsed_time = end_time - self.start_time  # 计算压测持续时间
    #     # print(f"Total time of this period: {elapsed_time} seconds")
    #     # total_rps = self.environment.runner.stats.total_rps()  # 整个压测期间的每秒请求数
    #     # print(f"Total RPS during this period: {total_rps}")


# 启动策略：逐步负载策略每隔30秒新增启动10个用户
class MyCustomShape(LoadTestShape):
    '''
        spawn_rate -- 用户在每一步的停止/启动的多少用户数
        time_limit -- 时间限制压测的执行时长
    '''
    time_limit = invoke_data_length * (max_request_time + single_stop_duration)  # 压测的执行时长,这个随便设的,得足够大
    spawn_rate = 100

    def tick(self):
        run_time = self.get_run_time()
        # 需要看当前时间是否在压测的时间段内
        is_in_test_duration = (run_time % (single_test_duration + single_stop_duration)) < single_test_duration

        if run_time < self.time_limit and is_in_test_duration:
            index = int((int(run_time / pressure_test_interval) + 1) % invoke_data_length)

            if index >= invoke_data_length:  # 如果超过了数据的长度,就停止压测
                return None

            user_count = int(invoke_data.at[index, 0])
            create_time = pendulum.now(TIME_ZONE)
            print(f"Current time: {create_time}, user count: {user_count}")
            sql = f"insert into request_cnt(create_time, request_cnt) values('{create_time}', {user_count})"
            db.CreateData(sql)
            # if user_count > 10:
            #     user_count = user_count // 10
            return (user_count, self.spawn_rate)
        elif run_time < self.time_limit and not is_in_test_duration:
            return (0, self.spawn_rate)

        return None
