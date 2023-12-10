import sched
import time
import threading
import pymysql


def your_function():
    global last_request_cnt, current_request_cnt
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

            print(f"20s内的请求数为: {temp}")
            # 更新全局变量
            last_request_cnt = current_request_cnt



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
    interval = 20  # 间隔时间，单位为秒
    scheduler.enter(interval, 1, scheduler_func, (scheduler, interval, your_function))

    # 两个全局变量
    last_request_cnt = 0
    current_request_cnt = 0


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
