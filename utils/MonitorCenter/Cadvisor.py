import time
from statistics import mean

from utils.MonitorCenter.PrometheusManager import PrometheusManager, PrometheusCannotQuery


# 对应Cadvisor的接口,监控容器级别的资源信息

# 所有的getRate函数均返回一个元组，目标是30s内的平均值和一个列表
# 第一个元素为平均值
# 第二个元素为一个列表,列表中的元素为一个列表,每个列表中的第一个元素为时间戳,第二个元素为对应的值


class Cadvisor:
    def __init__(self, promManager: PrometheusManager):
        self.promManager = promManager

    def getStaticInfoFromPod(self, pod: str):
        '''获取pod的静态信息'''
        res = dict()
        try:
            res['node'] = self.getNodeFromPod(pod)

            res['status'] = 'success'
        except PrometheusCannotQuery:
            res['status'] = 'error'
        return res

    def getDynamicInfoFromPod(self, pod: str):
        '''获取pod的动态信息'''
        end = time.time()
        res = dict()
        try:
            res['cpuRate'] = self.getCPURateTimely(pod, end)
            res['memRate'] = self.getMemRateTimely(pod, end)

            res['status'] = 'success'
        except PrometheusCannotQuery:
            res['status'] = 'error'

        return res

    # pod的CPU占用率随时间变化 含时间变化
    def getCPURateTimely(self, pod: str, end: float):
        query = 'sum by(pod)(irate(container_cpu_usage_seconds_total{{pod=~"^{pod}.*"}}[30s]))*100'.format(
            pod=pod)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_cpu = mean([float(record[1]) for record in response])
        return average_cpu, [[record[0], float(record[1])] for record in response]

    # pod的内存占用随时间变化[容器当前内存使用量/容器最大内存使用量] 含时间变化

    def getMemRateTimely(self, pod: str, end: float):
        query = 'sum(container_memory_usage_bytes{{pod=~"^{pod}.*"}} ' \
                '/ container_memory_max_usage_bytes{{pod=~"^{pod}.*"}})/2'.format(
                    pod=pod)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_mem = mean([float(record[1]) for record in response])
        return average_mem, [[record[0], float(record[1])] for record in response]

    # pod所属的服务器节点

    def getNodeFromPod(self, pod: str):
        # query = 'kube_pod_info{{namespace="openfaas-fn", pod=~"^{pod}.*"}}'.format(
        #     pod=pod + '-')
        # 这里加了'-'后就不对了
        query = 'kube_pod_info{{namespace="knative-fn", pod=~"^{pod}.*"}}'.format(
            pod=pod)
        return self.promManager.query(query)['data'][0]['metric']['node']
