from PrometheusManager import PrometheusManager


# 对应kube-state-metrics的接口,监控集群级别(k8s集群)的资源信息

# 所有的getRate函数均返回一个元组，目标是30s内的平均值和一个列表
# 第一个元素为平均值
# 第二个元素为一个列表,列表中的元素为一个列表,每个列表中的第一个元素为时间戳,第二个元素为对应的值


class KubeStateMetrics:
    def __init__(self, promManager: PrometheusManager):
        self.promManager = promManager

    # k8s集群中的服务器-node-ip
    def getNodes(self):
        res = {'status': 'error', 'nodes': []}
        response = self.promManager.query('kube_node_info')
        res['status'] = response['status']
        res['nodes'] = [{
            'ip': record['metric']['internal_ip'],
            'node': record['metric']['node']
        } for record in response['data']]
        return res

    # 服务器节点上启动的pod
    def getPodsFromNode(self, node: str):
        res = {'status': 'error', 'pod_name': []}
        query = 'kube_pod_info{{namespace="openfaas-fn", node="{node}"}}'.format(
            node=node)
        response = self.promManager.query(query)
        res['status'] = response['status']
        res['pod_name'] = [record['metric']['pod'].split(
            '-')[0] for record in response['data']]
        return res

    # 集群中所有的pod
    def getPods(self):
        res = {'status': 'error', 'pods': []}
        response = self.promManager.query(
            'kube_pod_info{namespace="openfaas-fn"}')
        res['status'] = response['status']
        res['pods'] = [{
            'pod_name': record['metric']['pod'].split('-')[0],
            'pod_real_name': record['metric']['pod'],
            'node': record['metric']['node']
        } for record in response['data']]
        return res
