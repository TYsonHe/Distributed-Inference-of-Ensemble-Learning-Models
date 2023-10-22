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
        pass

    def getFuncColdStartCount(self, funcName):
        """
        Get the cold start counts of a function
        """
        pass

    def getFuncAvgColdStartTime(self, funcName):
        """
        Get the average cold start time of a function
        """
        pass
