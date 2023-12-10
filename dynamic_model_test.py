import sched
import time
import threading
import pymysql  # 假设你使用的是 MySQL 数据库


def your_function():
    # 在函数内部创建数据库连接
    global TIMERANGE, last_max_model_id, cur_max_model_id
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
            now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 60 * 60))
            before_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 60 * 60 - TIMERANGE))
            # 执行sql语句
            sql = f"SELECT \
                        model_id,metric_type,metric_value \
                    FROM \
                        performance_metrics \
                    WHERE \
                        create_time BETWEEN '{before_time}' AND '{now_time}' AND model_id <> 101 \
                    ORDER BY \
                        model_id;"
            cursor.execute(sql)
            # 获取结果
            results = cursor.fetchall()
            print(results)

            # 简单算法实现~
            # 按model_id计算mse的平均值
            model_mse = {}
            for result in results:
                model_id = result['model_id']
                metric_type = result['metric_type']
                metric_value = result['metric_value']
                if model_id not in model_mse:
                    model_mse[model_id] = []
                if metric_type == 'mse':
                    model_mse[model_id].append(metric_value)

            # 计算mse的平均值
            model_avg_mse = {}
            for model_id in model_mse:
                model_avg_mse[model_id] = sum(model_mse[model_id]) / len(model_mse[model_id])

            # 选出mse最小的model_id和最大的model_id
            min_model_id = min(model_avg_mse, key=model_avg_mse.get)
            max_model_id = max(model_avg_mse, key=model_avg_mse.get)

            # 更改weight前，先看看max是否和之前的一样
            if cur_max_model_id == max_model_id:
                # 检查models的数量
                num = len(model_avg_mse)
                if num <= 2:
                    print("models数量不足3个，即使表现差也不用更新weight")
                    return
                print("max_model_id没有变化，降至0")
                # 获得这个model_id的weight
                sql = f"SELECT \
                            weight \
                        FROM \
                            models_weight \
                        WHERE \
                            model_id = {max_model_id};"
                cursor.execute(sql)
                # 获取结果
                temp_weight = cursor.fetchone()

                # 执行sql语句
                sql = f"UPDATE models_weight \
                            SET weight = 0 \
                            WHERE model_id = {max_model_id};"
                cursor.execute(sql)
                conn.commit()
                # 保持其他model的weight之和为1
                sql = f"UPDATE models_weight \
                            SET weight = weight + {float(temp_weight['weight']) / (num - 1)} \
                            WHERE model_id <> {max_model_id};"
                cursor.execute(sql)
                conn.commit()
                return
            else:
                # 更新全局变量
                last_max_model_id = cur_max_model_id
                cur_max_model_id = max_model_id
            # 连接数据库，改变weight
            # 执行sql语句，先获取当前的weight
            sql = f"SELECT \
                        model_id,weight \
                    FROM \
                        models_weight \
                    WHERE \
                        model_id = {min_model_id} OR model_id = {max_model_id};"
            cursor.execute(sql)
            # 获取结果
            model_weights = cursor.fetchall()
            print(f"更改前的model_weights: {model_weights}")

            # 更改weight
            # 更改权重25%
            temp = 0.0
            for each in model_weights:
                if each['model_id'] == max_model_id:
                    temp = float(each['weight']) * 0.25
                    break
            # min_model_id的weight增加temp, max_model_id的weight减少temp
            sql = f"UPDATE models_weight \
                        SET weight = weight + {temp} \
                        WHERE model_id = {min_model_id};"
            cursor.execute(sql)
            conn.commit()
            sql = f"UPDATE models_weight \
                        SET weight = weight - {temp} \
                        WHERE model_id = {max_model_id};"
            cursor.execute(sql)
            conn.commit()

            # 更改后的weight
            sql = f"SELECT \
                        model_id,weight \
                    FROM \
                        models_weight \
                    WHERE \
                        model_id = {min_model_id} OR model_id = {max_model_id};"
            cursor.execute(sql)
            # 获取结果
            model_weights = cursor.fetchall()
            print(f"更改后的model_weights: {model_weights}")


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
    interval = 60  # 间隔时间，单位为秒
    scheduler.enter(interval, 1, scheduler_func, (scheduler, interval, your_function))

    # 全局变量区
    last_max_model_id = -1
    cur_max_model_id = -2

    TIMERANGE = 60  # 时间范围，单位为秒


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
