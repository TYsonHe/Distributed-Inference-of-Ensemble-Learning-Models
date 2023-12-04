import time
import threading
import requests
import pymysql
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def process_request():
    # 获取查询参数
    req = request.get_json()
    input_str = req["input_str"]
    y_true = req["y_true"]
    print(input_str)
    print(y_true)
    # 从数据库中获取模型信息
    # 1.连接数据库
    conn = pymysql.connect(
        host='10.60.150.177',
        user='root',
        password='123456',
        db='model_historical_error',
        port=3306,
        charset='utf8'
    )
    # 2.创建游标
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    # 3.执行sql语句
    sql = "SELECT \
                models.model_id, models.model_name,models.model_type, models_weight.weight as model_weight \
           FROM \
                models \
           JOIN \
                models_weight ON models.model_id = models_weight.model_id \
           WHERE \
                models_weight.weight > 0;"

    cursor.execute(sql)
    # 4.获取结果
    models = cursor.fetchall()
    print(models)

    # 5.调用模型
    results = []

    def call_model(model: dict, input_str):
        # 1.获取模型信息
        model_id = model['model_id']
        model_name = model['model_name']
        model_weight = model['model_weight']
        model_type = model['model_type']
        create_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 2.调用模型
        url = 'http://10.60.150.177:32619/'
        headers = {
            'Host': f'{model_name}.knative-fn.knative.example.com ',
            'Content-Type': 'text/plain',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        data = input_str
        response = requests.request(
            "POST", url=url, headers=headers, data=data)
        # 3.获取模型返回结果
        print(response.text)
        model_result = response.text
        result = dict()
        result['model_id'] = model_id
        result['model_name'] = model_name
        result['model_weight'] = model_weight
        result['model_type'] = model_type
        result['model_result'] = model_result
        result['y_true'] = y_true
        result['create_time'] = create_time
        results.append(result)
        # 4.将模型返回结果送入数据库
        # new_url = 'http://10.60.150.177:8001/'
        # new_url = 'http://localhost:8001/'
        # new_headers = {
        #     'Content-Type': 'application/json',
        #     'Accept': '*/*',
        #     'Connection': 'keep-alive'
        # }
        # new_data = {
        #     'model_id': model_id,
        #     'model_result': model_result,
        #     'y_true': y_true,
        #     'create_time': create_time
        # }
        # new_response = requests.request(
        #     "POST", url=new_url, headers=new_headers, json=new_data)
        # print(new_response.status_code)
        # if new_response.status_code == 200:
        #     print('模型感知器接收成功')

    # 5.1 创建线程
    threads = []
    for model in models:
        t = threading.Thread(target=call_model, args=(model, input_str))
        threads.append(t)
    # 5.2 启动线程
    for t in threads:
        t.start()
    # 5.3 等待线程结束
    for t in threads:
        t.join()

    # 7.计算集成结果
    ensemble_result = 0
    for result in results:
        ensemble_result += result['model_weight'] * \
                           float(result['model_result'])
    # results.append({'ensemble_result': ensemble_result})

    print(results)

    # 将结果送入数据库
    for result in results:
        sql = f'INSERT INTO models_results (model_id,model_result,y_true,create_time) VALUES ({result["model_id"]},"{result["model_result"]}","{result["y_true"]}","{result["create_time"]}")'
        cursor.execute(sql)
        conn.commit()

    sql = f'INSERT INTO models_results (model_id,model_result,y_true,create_time) VALUES (101,"{ensemble_result}","{results[0]["y_true"]}","{results[0]["create_time"]}")'
    cursor.execute(sql)
    conn.commit()

    # 关闭游标和连接
    cursor.close()
    conn.close()

    # 8.返回结果
    return f'{results}'


# 测试

if __name__ == '__main__':
    app.run()
