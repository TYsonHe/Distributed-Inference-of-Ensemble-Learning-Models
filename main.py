from utils.MonitorCenter.MonitorCenter import MonitorCenter
from utils.FuncMonitor import FuncMonitor

if __name__ == "__main__":
    monitorCenter = MonitorCenter(
        'configs\monitor.yml')
    monitorCenter.loadConfig()
    funcMonitor = FuncMonitor(monitorCenter)
    funcList = funcMonitor.getFuncList()
    print(funcList)
