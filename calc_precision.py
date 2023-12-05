from utils.PrecisionSensor.PrecisionSensor import PrecisionSensor
from utils.CrudDb import CrudDb
import time

precision_sensor = PrecisionSensor()
db = CrudDb('configs\db.yml')

if __name__ == '__main__':
    # 这里接受到监控中心信号，准备计算精度
    # 1. 从数据库中读取数据

    # 还有可能是serverful
    type = 'serverless'
    now_time = '2023-12-24 00:00:00'
    # now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # 获取15s前的时间
    before_time = '2023-11-23 00:00:00'
    # before_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 15))

    if type == 'serverless':
        sql = f"SELECT model_id, model_result, y_true \
               FROM \
		            models_results \
               WHERE \
		            create_time BETWEEN '{before_time}' AND '{now_time}' \
               ORDER BY \
		            model_id;"
    else:
        sql = f"SELECT model_id, model_result, y_true \
                FROM \
                      svc_models_results \
                WHERE \
                      create_time BETWEEN '{before_time}' AND '{now_time}' \
                ORDER BY \
                      model_id;"

    results = db.RetrieveData(sql)
    print(results)

    # 2. 计算精度
    # 按照model_id提取result中所有的model_result和y_true
    # 每个result是一个元组，包含model_id, model_result, y_true
    # 还要进行类型转换

    result_dict = {}

    for entry in results:
        model_id = entry['model_id']
        model_result = entry['model_result']
        y_true = entry['y_true']

        if model_id not in result_dict:
            result_dict[model_id] = {'model_results': [], 'y_true': []}

        result_dict[model_id]['model_results'].append(float(model_result))
        result_dict[model_id]['y_true'].append(float(y_true))

    print(result_dict)
    # 等会写入数据库要加上的time, 每轮计算精度的时间都要一致
    create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for model_id, result in result_dict.items():
        model_results = result['model_results']
        y_true = result['y_true']
        precision_sensor.getData(y_true, model_results)
        precision_sensor.setMetricsModel('regression')
        precision_results = precision_sensor.calcPrecision()
        print(precision_results)
        # 3. 将精度写入数据库

        for metric_type, value in precision_results.items():
            print(metric_type, value)
            if type == 'serverless':
                sql = f"INSERT INTO performance_metrics(model_id, metric_type, metric_value, create_time) \
                        VALUES({model_id}, '{metric_type}', {value}, '{create_time}');"
            else:
                sql = f"INSERT INTO svc_performance_metrics(model_id, metric_type, metric_value, create_time) \
                        VALUES({model_id}, '{metric_type}', {value}, '{create_time}');"
            db.CreateData(sql)

    print('PrecisionSensor: precision is calculated and written to database.')

    # 是否将算法填入……

    pass
