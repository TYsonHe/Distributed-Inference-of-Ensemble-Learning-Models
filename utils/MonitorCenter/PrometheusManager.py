import json

import requests


# 提供Prometheus的API接口，PromQL的统一查询接口


class PrometheusManager:
    def __init__(self, ip: str):
        self.ip = ip
        self.apiQuery = 'http://' + ip + '/api/v1/query'
        self.apiQueryRange = 'http://' + ip + '/api/v1/query_range'

    def testConnection(self):
        '''测试与Prometheus的连接是否正常'''
        res = requests.get(self.apiQuery, params={'query': 'up'}, timeout=5)
        if res.status_code == 200:
            return True
        else:
            return False

    def query(self, query: str):
        '''查询PromQL,返回查询结果
        一般是瞬时值和确定的信息'''
        res = {
            'status': 'error',
            'data': '',
        }
        response = requests.get(self.apiQuery, params={'query': query})
        if response.status_code == 200:
            response_json = json.loads(response.text)
            res['status'] = response_json['status']
            res['data'] = response_json['data']['result']
        else:
            print('请求错误,错误代码为' + str(response.status_code))

        return res

    def queryRange(self, query: str, end: float, ahead: int = 60, step: int = 1):
        '''
        在一定时间范围内,以一定间隔重复查询query
        时间范围为[end-ahead, end],ahead表示提前的秒数
        step:时间间隔，以秒为单位
        '''
        start = end - ahead
        res = {
            'status': 'error',
            'data': '',
        }
        response = requests.get(self.apiQueryRange, {
            'query': query, 'start': start, 'end': end, 'step': step})
        if response.status_code == 200:
            response_json = json.loads(response.text)
            res['status'] = response_json['status']
            res['data'] = response_json['data']['result']
        else:
            print('请求错误,错误代码为' + str(response.status_code))
            raise PrometheusCannotQuery("查询失败")

        return res


# 自定义异常：Prometheus查询异常


class PrometheusCannotQuery(Exception):
    def __init__(self, error_info):
        super(PrometheusCannotQuery, self).__init__(error_info)
        self.error_info = error_info

    def __str__(self):
        return self.error_info
