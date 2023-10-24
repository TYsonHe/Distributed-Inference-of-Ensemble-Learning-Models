from utils.MonitorCenter.MonitorCenter import MonitorCenter
import requests


class FuncMonitor:
    def __init__(self, monitorCenter: MonitorCenter):
        self.monitorCenter = monitorCenter

    def getFuncList(self):
        url = 'http://'+self.monitorCenter.openFaaSGateway + '/system/functions'
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, auth=(
            self.monitorCenter.openFaaSUser, self.monitorCenter.openFaaSPassword), headers=headers)
        funcList = []
        for func in response.json():
            funcList.append(func['name'])
        return funcList

    def getFuncInvocationTotal(self, funcName):
        url = 'http://'+self.monitorCenter.openFaaSGateway + '/system/function/'+funcName
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, auth=(
            self.monitorCenter.openFaaSUser, self.monitorCenter.openFaaSPassword), headers=headers)
        return response.json()['invocationCount']

    def getFuncRequestTotal(self, funcName):
        '''
        Get the total number of requests of a function
        '''
        query = 'gateway_function_requests_total{{function_name=~"{funcName}\\\\..*"}}'.format(
            funcName=funcName)
        res = self.monitorCenter.promManager.query(
            query)['data'][0]['value'][1]
        return res

    def getFuncColdStartCount(self, funcName):
        """
        Get the cold start counts of a function
        """
        query = 'gateway_function_cold_start_seconds_count{{function_name=~"{funcName}\\\\..*"}}'.format(
            funcName=funcName)
        print(query)
        res = self.monitorCenter.promManager.query(
            query)['data'][0]['value'][1]
        return res

    def getFuncAvgColdStartTime(self, funcName):
        """
        Get the average cold start time of a function
        """
        function_name_pattern = funcName+"\\\\..*"
        query = 'gateway_function_cold_start_seconds_sum{{function_name=~"{0}"}} / gateway_function_cold_start_seconds_count{{function_name=~"{0}"}}'.format(
            function_name_pattern)
        res = self.monitorCenter.promManager.query(
            query)['data'][0]['value'][1]
        return res
