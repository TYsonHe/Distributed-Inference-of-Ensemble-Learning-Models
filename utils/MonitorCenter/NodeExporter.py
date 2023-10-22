import time
from statistics import mean

from utils.MonitorCenter.PrometheusManager import PrometheusManager, PrometheusCannotQuery


# 对应node_exporter的接口,监控服务器(node节点)物理器级别的资源信息


class NodeExporter:
    def __init__(self, promManager: PrometheusManager):
        self.promManager = promManager

    def getDynamicInfoFromNode(self, node: str):
        '''获取node的各项动态信息
        返回一个字典,包含各项信息
        '''
        end = time.time()
        res = dict()
        try:
            res['cpuRateAvg'], res['cpuRate'] = self.getCPURateTimely(
                node, end)
            res['diskRateAvg'], res['diskRate'] = self.getDiskRateTimely(
                node, end)
            res['diskReadAvg'], res['diskRead'] = self.getDiskReadTimely(
                node, end)
            res['diskWriteAvg'], res['diskWrite'] = self.getDiskWriteTimely(
                node, end)
            res['memRateAvg'], res['memRate'] = self.getMemRateTimely(
                node, end)
            res['networkUpAvg'], res['networkUP'] = self.getNetworkUpLoadTimely(
                node, end)
            res['networkDownAvg'], res['networkDown'] = self.getNetWorkDownloadTimely(
                node, end)

            res['status'] = 'success'
        except PrometheusCannotQuery:
            res['status'] = 'error'

        return res

    def getCPURateTimely(self, node: str, end: float):
        '''获取node的CPU使用率随时间变化'''
        query = '100-(avg by(instance)' \
                '(irate(node_cpu_seconds_total{{mode="idle",instance="{node}"}}[30s]))*100)'.format(
                    node=node)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_cpu_rate = mean([float(record[1]) for record in response])
        return average_cpu_rate, [[record[0], float(record[1])] for record in response]

    def getDiskRateTimely(self, node: str, end: float):
        '''获取node的磁盘使用率随时间变化'''
        query = '100 - ' \
                'node_filesystem_free_bytes{{mountpoint = "/", instance="{node}", ' \
                'fstype!~"rootfs|selinuxfs|autofs|rpc_pipefs|tmpfs|udev|none|devpts|sysfs|debugfs|fuse.*"}} /' \
                'node_filesystem_size_bytes{{mountpoint = "/", instance="{node}", ' \
                'fstype!~"rootfs|selinuxfs|autofs|rpc_pipefs|tmpfs|udev|none|devpts|sysfs|debugfs|fuse.*"}}' \
                ' * 100'.format(node=node)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_disk_rate = mean([float(record[1]) for record in response])
        return average_disk_rate, [[record[0], float(record[1])] for record in response]

    def getDiskReadTimely(self, node: str, end: float):
        '''获取node的磁盘读取速率随时间变化'''
        query = 'sum by(instance)(irate(node_disk_read_bytes_total{{instance="{node}"}}[30s])' \
                '/1024)'.format(node=node)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_disk_read = mean([float(record[1]) for record in response])
        return average_disk_read, [[record[0], float(record[1])] for record in response]

    def getDiskWriteTimely(self, node: str, end: float):
        '''获取node的磁盘写入速率随时间变化'''
        query = 'sum by(instance)(irate(node_disk_written_bytes_total{{instance="{node}"}}[30s])' \
                '/1024)'.format(node=node)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_disk_write = mean([float(record[1]) for record in response])
        return average_disk_write, [[record[0], float(record[1])] for record in response]

    def getMemRateTimely(self, node: str, end: float):
        '''获取node的内存使用率随时间变化'''
        query = '100 -(node_memory_MemFree_bytes{{instance="{node}"}} ' \
                '+ node_memory_Cached_bytes{{instance="{node}"}}' \
                '+node_memory_Buffers_bytes{{instance="{node}"}})' \
                '/node_memory_MemTotal_bytes{{instance="{node}"}}*100'.format(
                    node=node)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_mem_rate = mean([float(record[1]) for record in response])
        return average_mem_rate, [[record[0], float(record[1])] for record in response]

    def getNetworkUpLoadTimely(self, node: str, end: float):
        '''获取node的网络上传速率随时间变化'''
        query = 'sum by(instance)' \
                '(irate(node_network_transmit_bytes_total{{device!="lo",instance="{node}"}}[30s])' \
                '/1024)'.format(node=node)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_network_upload = mean(
            [float(record[1]) for record in response])
        return average_network_upload, [[record[0], float(record[1])] for record in response]

    def getNetWorkDownloadTimely(self, node: str, end: float):
        '''获取node的网络下载速率随时间变化'''
        query = 'sum by(instance)' \
                '(irate(node_network_receive_bytes_total{{device!="lo",instance="{node}"}}[30s])' \
                '/1024)'.format(node=node)
        response = self.promManager.queryRange(query, end)['data'][0]['values']
        average_network_download = mean(
            [float(record[1]) for record in response])
        return average_network_download, [[record[0], float(record[1])] for record in response]
