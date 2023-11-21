'''
Author: yingxin wang
Date: 2023-11-16 15:17:56
LastEditors: yingxin wang
LastEditTime: 2023-11-17 21:32:59
Description: 实现缩放中心的功能
'''
import yaml
import schedule
import time
import math

from utils.ScalingCenter.KubeApiServer import KubeApiServer
from utils.ScalingCenter.ScalingMetrics import ScalingMetrics

class ScalingCenter:
    def __init__(self, kube_api_server: KubeApiServer, scaling_metrics: ScalingMetrics):
        self.kube_api_server = kube_api_server
        self.scaling_metrics = scaling_metrics
        
        #get all model names
        with open('configs\models2.yml', 'r') as file:
            yaml_data= yaml.safe_load(file)
        self.model_names=self._extractModelNames(yaml_data)
        self.namespace='openfaas-fn'

        self.can_scale = True
        self.last_scale_time=0
    
    def _extractModelNames(self,data):
        model_names = []
        if 'main_model' in data:
            for model in data['main_model']:
                model_names.append(model['name'])
                if 'base_learners' in model:
                    for base_learner in model['base_learners']:
                        model_names.append(base_learner['name'])
        return model_names
    

    def _autoScaleBasedOnRequests(self, model_name, min_replica_count,max_replica_count,threshold):
        if False==self.can_scale:  #如果不能缩放，直接返回
            return 

        request_count = float(self.scaling_metrics.getFunctionRequestsTotal(self.namespace,model_name))
        replica_count=int(self.kube_api_server.getDeploymentReplicas(self.namespace, model_name))

        target_replica_count=replica_count
        if request_count is None:
            print(f"Error getting request count for {model_name}")
            return
        elif request_count == 0: #没有请求，缩减至0
            target_replica_count=0
        elif request_count > threshold and self.can_scale: #大于阈值，扩容
            target_replica_count = min(max_replica_count, math.ceil(request_count / threshold))
        elif request_count < threshold and self.can_scale:  #小于阈值，缩容
            target_replica_count = max(min_replica_count, math.ceil(request_count / threshold) ,1) #最少一个副本，因为至少是有请求的

        print(f"{model_name} : Current request count {request_count}, current replica count {replica_count}, target replica count {target_replica_count}")
        if target_replica_count == replica_count:    #如果目标副本数和当前副本数相同，不做操作，直接返回
            return
        
        #更新副本数
        self.kube_api_server.updateDeploymentReplicas(self.namespace, model_name, target_replica_count)
        print('')
        print(f"Deployment {model_name} in namespace {self.namespace} updated to {target_replica_count} replicas")
        self.can_scale=False
        self.last_scale_time = time.time()

    #orignal auto scale
    def autoScaleOrignal(self):
        polling_interval=1
        cooldown_period=5
        min_replica_count=0
        max_replica_count=20
        threshold=0.5

        # for model_name in self.model_names:
        #     schedule.every(polling_interval).seconds.do(self._autoScaleBasedOnRequests, model_name, min_replica_count,max_replica_count,threshold)
        schedule.every(polling_interval).seconds.do(self._autoScaleBasedOnRequests, 'yolo-darknet', min_replica_count,max_replica_count,threshold)

        while True:
            schedule.run_pending()
            # 检查是否经过了冷却期
            current_time = time.time()
            if current_time - self.last_scale_time >= cooldown_period:
                self.can_scale = True
            time.sleep(1)
