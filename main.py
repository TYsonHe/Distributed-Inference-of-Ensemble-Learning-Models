from utils.MonitorCenter.MonitorCenter import MonitorCenter
from utils.FuncMonitor import FuncMonitor

if __name__ == "__main__":
    monitorCenter = MonitorCenter(
        'configs\monitor.yml')
    monitorCenter.loadConfig()
    funcMonitor = FuncMonitor(monitorCenter)
    funcList = funcMonitor.getFuncList()
    print(funcList)
    print(funcMonitor.getFuncReplicas('nodeinfo'))
    print(funcMonitor.getFuncInvocationRange('nodeinfo', '30m'))
    print(funcMonitor.getFuncRequestRange('nodeinfo', '30m'))
    print(funcMonitor.getFuncAvgColdStartTimeRange('nodeinfo', '30m'))
    print(funcMonitor.getFuncInFlightRange('nodeinfo', '30m'))
