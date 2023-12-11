import sched
import time
import threading
import pymysql
from utils.PrecisionSensor.PrecisionSensor import PrecisionSensor
from utils.MonitorCenter.MonitorCenter import MonitorCenter
from utils.FuncMonitor import FuncMonitor


def your_function():
    global last_request_cnt, current_request_cnt, TYPE, THRESHOLD, TIMERANGE
    # 在这里定义你的函数内容
    try:
        conn = pymysql.connect(
            host='10.60.150.177',
            user='root',
            password='123456',
            db='model_historical_error',
            port=3306,
            charset='utf8'
        )
        with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            if TYPE == 'serverless':
                monitor_center = MonitorCenter('.\configs\monitor.yml')
                func_monitor = FuncMonitor(monitor_center)
                # 注意类型转换
                current_request_cnt = float(func_monitor.get_kn_request_cnt('em-fn', TIMERANGE))
                temp = current_request_cnt
                print(f"{TIMERANGE}内的请求率为: {temp}")
            else:
                # 执行sql语句
                sql = "SELECT \
                            request_cnt \
                       FROM \
                            svc_model_cnt \
                       WHERE \
                            model_id = 101;"
                cursor.execute(sql)
                # 获取结果
                result = cursor.fetchone()
                current_request_cnt = result['request_cnt']

                temp = current_request_cnt - last_request_cnt

                print(f"{TIMERANGE}内的请求数为: {temp}")
                # 更新全局变量
                last_request_cnt = current_request_cnt

            if temp <= THRESHOLD and TYPE == 'serverful':
                print(f"{TIMERANGE}请求过低,低于{THRESHOLD}, 不用计算精度")
                # 无请求，不用计算精度
                return
            elif temp <= 2.5 and TYPE == 'serverless':
                print(f"{TIMERANGE}请求率过低,低于2.5, 不用计算精度")
                # 无请求，不用计算精度
                return
            else:
                precision_sensor = PrecisionSensor()
                # 注意，这里的时间是北京时间，要减去8小时才是UTC时间
                now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 60 * 60))
                print(f"now_time: {now_time}")
                # 获取20s前的时间
                before_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 60 * 60 - 60))
                print(f"before_time: {before_time}")
                if TYPE == 'serverless':
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
                cursor.execute(sql)
                # 获取结果
                results = cursor.fetchall()
                # print(f"get results successfully")

                result_dict = {}
                for entry in results:
                    model_id = entry['model_id']
                    model_result = entry['model_result']
                    y_true = entry['y_true']

                    if model_id not in result_dict:
                        result_dict[model_id] = {'model_results': [], 'y_true': []}

                    result_dict[model_id]['model_results'].append(float(model_result))
                    result_dict[model_id]['y_true'].append(float(y_true))

                # 等会写入数据库要加上的time, 每轮计算精度的时间都要一致
                create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 60 * 60))
                for model_id, result in result_dict.items():
                    model_results = result['model_results']
                    y_true = result['y_true']
                    precision_sensor.getData(y_true, model_results)
                    precision_sensor.setMetricsModel('regression')
                    precision_results = precision_sensor.calcPrecision()
                    print(f"precision_results: {precision_results}")
                    # 3. 将精度写入数据库

                    for metric_type, value in precision_results.items():
                        if TYPE == 'serverless':
                            sql = f"INSERT INTO performance_metrics(model_id, metric_type, metric_value, create_time) \
                                    VALUES({model_id}, '{metric_type}', {value}, '{create_time}');"
                        else:
                            sql = f"INSERT INTO svc_performance_metrics(model_id, metric_type, metric_value, create_time) \
                                    VALUES({model_id}, '{metric_type}', {value}, '{create_time}');"
                        cursor.execute(sql)
                        conn.commit()

                print('PrecisionSensor: precision is calculated and written to database.')
                print(f'update time: {create_time}')



    except Exception as e:
        print(f"数据库操作出错: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()


def scheduler_func(scheduler, interval, action):
    scheduler.enter(interval, 1, scheduler_func, (scheduler, interval, action))
    action()


if __name__ == "__main__":

    # 创建一个调度器
    scheduler = sched.scheduler(time.time, time.sleep)

    # 设置定时任务
    interval = 60  # 间隔时间，单位为秒, 1分钟与下面TIMERANGE对应
    scheduler.enter(interval, 1, scheduler_func, (scheduler, interval, your_function))

    # 两个全局变量
    last_request_cnt = 0
    current_request_cnt = 0

    TYPE = 'serverless'
    THRESHOLD = 80
    TIMERANGE = '1m'


    # 创建守护线程
    def daemon_thread():
        scheduler.run()


    thread = threading.Thread(target=daemon_thread, daemon=True)
    thread.start()

    # 在这里可以继续写主程序的逻辑，守护线程会在后台执行定时任务
    try:
        while True:
            # 在这里可以添加主程序的逻辑
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序结束")
