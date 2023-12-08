from utils.MonitorCenter.MonitorCenter import MonitorCenter
import requests


class FuncMonitor:
    def __init__(self, monitorCenter: MonitorCenter):
        self.monitorCenter = monitorCenter

    # def getFuncList(self):
    #     url = 'http://'+self.monitorCenter.openFaaSGateway + '/system/functions'
    #     headers = {"Content-Type": "application/json"}
    #     response = requests.get(url, auth=(
    #         self.monitorCenter.openFaaSUser, self.monitorCenter.openFaaSPassword), headers=headers)
    #     funcList = []
    #     for func in response.json():
    #         funcList.append(func['name'])
    #     return funcList

    # def getFuncReplicas(self, funcName):
    #     query = 'gateway_service_count{{function_name=~"{funcName}\\\\..*"}}'.format(
    #         funcName=funcName)
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncInvocationTotal(self, funcName):
    #     query = 'sum (gateway_function_invocation_total{{function_name=~"{funcName}\\\\..*"}})'.format(
    #         funcName=funcName)
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncInvocationRange(self, funcName, timeRange: str, is_offset=False, offset=''):
    #     '''
    #     Get the invocation count of a function in a time range
    #     time range example: 1s 1h 30m 1d
    #     '''
    #     query = 'increase(gateway_function_invocation_total{{function_name=~"{funcName}\\\\..*"}}[{timeRange}]'.format(
    #         funcName=funcName, timeRange=timeRange)
    #     if is_offset:
    #         query = query + ' offset ' + str(offset)
    #     query = query + ')'
    #     # print(query)
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncRequestTotal(self, funcName):
    #     '''
    #     Get the total number of requests of a function
    #     '''
    #     query = 'gateway_function_requests_total{{function_name=~"{funcName}\\\\..*"}}'.format(
    #         funcName=funcName)
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncRequestRange(self, funcName, timeRange: str, is_offset=False, offset=''):
    #     '''
    #     Get the total number of requests of a function in a time range
    #     time range example: 1s 1h 30m 1d
    #     '''
    #     query = 'increase(gateway_function_requests_total{{function_name=~"{funcName}\\\\..*"}}[{timeRange}]'.format(
    #         funcName=funcName, timeRange=timeRange)
    #     if is_offset:
    #         query = query + ' offset ' + str(offset)
    #     query = query + ')'
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncColdStartCount(self, funcName):
    #     """
    #     Get the cold start counts of a function
    #     """
    #     query = 'gateway_function_cold_start_seconds_count{{function_name=~"{funcName}\\\\..*"}}'.format(
    #         funcName=funcName)
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncColdStartCountRange(self, funcName, timeRange: str, is_offset=False, offset=''):
    #     '''
    #     Get the cold start counts of a function in a time range
    #     time range example: 1s 1h 30m 1d
    #     '''
    #     query = 'increase(gateway_function_cold_start_seconds_count{{function_name=~"{funcName}\\\\..*"}}[{timeRange}]'.format(
    #         funcName=funcName, timeRange=timeRange)
    #     if is_offset:
    #         query = query + ' offset ' + str(offset)
    #     query = query + ')'
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncAvgColdStartTime(self, funcName):
    #     """
    #     Get the average cold start time of a function
    #     """
    #     function_name_pattern = funcName+"\\\\..*"
    #     query = 'gateway_function_cold_start_seconds_sum{{function_name=~"{0}"}} / gateway_function_cold_start_seconds_count{{function_name=~"{0}"}}'.format(
    #         function_name_pattern)
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncAvgColdStartTimeRange(self, funcName, timeRange: str, is_offset=False, offset=''):
    #     """
    #     Get the average cold start time of a function in a time range
    #     time range example: 1s 1h 30m 1d
    #     """
    #     function_name_pattern = funcName+"\\\\..*"
    #     query = 'increase(gateway_function_cold_start_seconds_sum{{function_name=~"{0}"}}[{1}]) / increase(gateway_function_cold_start_seconds_count{{function_name=~"{0}"}}[{1}])'.format(
    #         function_name_pattern, timeRange)
    #     if is_offset:
    #         query = 'increase(gateway_function_cold_start_seconds_sum{{function_name=~"{0}"}}[{1}] offset {2}) / increase(gateway_function_cold_start_seconds_count{{function_name=~"{0}"}}[{1}] offset {2})'.format(
    #             function_name_pattern, timeRange, offset)
    #     # print(query)
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     if res == 'NaN':
    #         return 'Function cold start time is not available in this time range'
    #     return res

    # def getFuncInFlight(self, funcName):
    #     """
    #     Get the in-flight requests of a function
    #     """
    #     query = 'gateway_function_in_flight{{function_name=~"{funcName}\\\\..*"}}'.format(
    #         funcName=funcName)
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res

    # def getFuncInFlightRange(self, funcName, timeRange: str, is_offset=False, offset=''):
    #     '''
    #     Get the in-flight requests of a function in a time range
    #     time range example: 1s 1h 30m 1d
    #     '''
    #     query = 'increase(gateway_function_in_flight{{function_name=~"{funcName}\\\\..*"}}[{timeRange}]'.format(
    #         funcName=funcName, timeRange=timeRange)
    #     if is_offset:
    #         query = query + ' offset ' + str(offset)
    #     query = query + ')'
    #     res = self.monitorCenter.promManager.query(
    #         query)['data'][0]['value'][1]
    #     return res
