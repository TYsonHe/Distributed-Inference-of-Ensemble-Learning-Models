from utils.PrecisionSensor.PrecisionSensor import PrecisionSensor
from utils.CrudDb import CrudDb
from flask import Flask, request

app = Flask(__name__)

precision_sensor = PrecisionSensor()
db = CrudDb('configs\db.yml')


@app.route('/', methods=['POST'])
def process_request():
    # 获取查询参数
    req = request.get_json()
    model_id = req["model_id"]
    model_result = req["model_result"]
    create_time = req["create_time"]
    y_true = req["y_true"]

    # 存储到数据库
    # 3.执行sql语句
    # 一共有5个metric_type
    query = f'insert into models_results (model_id, model_result,y_true,create_time) values ({model_id}, "{model_result}", "{y_true}","{create_time}")'
    # print(query)
    db.CreateData(query)

    return 'ok'


# test
if __name__ == '__main__':
    app.run(host='localhost', port=8001)
