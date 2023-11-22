from utils.MonitorCenter.MonitorCenter import MonitorCenter
from utils.FuncMonitor import FuncMonitor
from utils.ScalingCenter.ScalingMetrics import ScalingMetrics
from utils.ScalingCenter.ScalingCenter import ScalingCenter
from utils.ScalingCenter.KubeApiServer import KubeApiServer
from utils.RequestEmitter.RequestEmitter import RequestEmitter

if __name__ == "__main__":
    monitorCenter = MonitorCenter(
        'configs\monitor.yml')
    funcMonitor = FuncMonitor(monitorCenter)
    funcList = funcMonitor.getFuncList()
    print(funcList)
    print(funcMonitor.getFuncReplicas('nodeinfo'))
    print(funcMonitor.getFuncInvocationRange('nodeinfo', '30m', True, '1d'))
    print(funcMonitor.getFuncInvocationRange('nodeinfo', '30m'))
    print(funcMonitor.getFuncRequestRange('nodeinfo', '30m', True, '1d'))
    print(funcMonitor.getFuncRequestRange('nodeinfo', '30m'))
    print(funcMonitor.getFuncAvgColdStartTimeRange(
        'nodeinfo', '30m', True, '1d'))
    print(funcMonitor.getFuncAvgColdStartTimeRange('nodeinfo', '30m'))
    print(funcMonitor.getFuncInFlightRange('nodeinfo', '30m', True, '1d'))
    print(funcMonitor.getFuncInFlightRange('nodeinfo', '30m'))

    # scaling_metrics=ScalingMetrics(monitorCenter)
    # kube_api_server=KubeApiServer()
    # scaling_center = ScalingCenter(kube_api_server, scaling_metrics)
    # scaling_center.autoScaleOrignal()

    # request_emitter=RequestEmitter()
    # request_emitter.initHttpRequest('http://10.60.150.177:31112/function/stock-predict','GET')
    # request_emitter.initData(False,False,'testDataSets/stockPredict/dji_x_test_full.csv')
    # #%%
    # request_emitter.loadTest(1,(1,9),2)