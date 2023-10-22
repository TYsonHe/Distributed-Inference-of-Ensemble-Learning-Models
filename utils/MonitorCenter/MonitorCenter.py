import yaml

from utils.MonitorCenter.Cadvisor import Cadvisor
from utils.MonitorCenter.KubeStateMetrics import KubeStateMetrics
from utils.MonitorCenter.NodeExporter import NodeExporter
from utils.MonitorCenter.PrometheusManager import PrometheusManager


class MonitorCenter:
    def __init__(self, configPath: str):
        self.configPath = configPath
        self.loadConfig()
        self.promManager = PrometheusManager(self.prometheusGateway)
        self.cadvisor = Cadvisor(self.promManager)
        self.nodeExporter = NodeExporter(self.promManager)
        self.kubeStateMetrics = KubeStateMetrics(self.promManager)

    def loadConfig(self):
        with open(self.configPath, 'r') as f:
            monitorCenterConfig = yaml.load(f, Loader=yaml.FullLoader)
        self.prometheusGateway = monitorCenterConfig['prometheusGateway']
        self.openFaaSGateway = monitorCenterConfig['openFaaSGateway']
        self.openFaaSUser = monitorCenterConfig['openFaaSBasicAuth']['user']
        self.openFaaSPassword = monitorCenterConfig['openFaaSBasicAuth']['password']


# test
if __name__ == "__main__":
    monitorCenter = MonitorCenter(
        'configs\monitor.yml')
    monitorCenter.loadConfig()
