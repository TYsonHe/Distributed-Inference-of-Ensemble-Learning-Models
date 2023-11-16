'''
Author: yingxin wang
Date: 2023-11-16 20:14:06
LastEditors: yingxin wang
LastEditTime: 2023-11-16 21:17:18
Description: 用于auto scaling的metrics
'''
from utils.MonitorCenter.MonitorCenter import MonitorCenter

class ScalingMetrics:
    def __init__(self, monitorCenter: MonitorCenter):
        self.monitorCenter = monitorCenter

    #获取网关一分钟接口总数
    def getFunctionRequestsTotal(self, namespace: str, deployment_name: str):
        query='sum (rate(gateway_function_requests_total{{function_name="{deployment_name}.{namespace}"}}[1m]))'.format(
                    deployment_name=deployment_name,namespace=namespace)
        res = self.monitorCenter.promManager.query(query)['data'][0]['value'][1]
        return res
    

if __name__ == "__main__":
    monitor_center = MonitorCenter(
        '..\..\configs\monitor.yml')
    scaling_metrics = ScalingMetrics(monitor_center)

    print(scaling_metrics.getFunctionRequestsTotal('yolo-darknet', 'openfaas-fn'))