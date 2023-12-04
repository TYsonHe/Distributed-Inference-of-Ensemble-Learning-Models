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

    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    sql = "SELECT \
		       svc_models.model_id, svc_models.model_name, svc_models_weight.weight as model_weight, svc_models.nodeport \
           FROM \
		       svc_models \
           JOIN \
		       svc_models_weight ON svc_models.model_id = svc_models_weight.model_id \
           WHERE \
		       svc_models_weight.weight > 0;"

    cursor.execute(sql)
    models = cursor.fetchall()
    print(models)

    results = []

    def call_model(model: dict, input_str: str):
        model_id = model["model_id"]
        model_name = model["model_name"]
        model_weight = model["model_weight"]
        nodeport = model["nodeport"]
        url = f"http://10.60.150.177:{nodeport}"
        create_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        data = input_str

        response = requests.post(url, data=data)
        print(response.text)
        model_result = response.text
        result = dict()
        result["model_id"] = model_id
        result["model_name"] = model_name
        result["model_weight"] = model_weight
        result["model_result"] = model_result
        result["create_time"] = create_time
        result["y_true"] = y_true
        results.append(result)

    threads = []
    for model in models:
        t = threading.Thread(target=call_model, args=(model, input_str))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    ensemble_result = 0
    for result in results:
        ensemble_result += result['model_weight'] * \
                           float(result['model_result'])

    # 将集成模型结果送入数据库

    for result in results:
        sql = f'INSERT INTO svc_models_results (model_id,model_result,y_true,create_time) VALUES ({result["model_id"]},"{result["model_result"]}","{result["y_true"]}","{result["create_time"]}")'
        cursor.execute(sql)
        conn.commit()

    sql = f'INSERT INTO svc_models_results (model_id,model_result,y_true,create_time) VALUES (101,"{ensemble_result}","{results[0]["y_true"]}","{results[0]["create_time"]}")'
    cursor.execute(sql)
    conn.commit()

    # 关闭游标和连接
    cursor.close()
    conn.close()

    # 8.返回结果
    return f'{results}'


if __name__ == '__main__':
    app.run()
