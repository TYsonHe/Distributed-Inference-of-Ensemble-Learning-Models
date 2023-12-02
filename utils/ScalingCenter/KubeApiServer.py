'''
Author: yingxin wang
Date: 2023-11-16 15:36:01
LastEditors: yingxin wang
LastEditTime: 2023-11-16 21:52:50
Description: kubernetes API服务组件
'''
from kubernetes import client, config


class KubeApiServer:
    def __init__(self):
        config.load_kube_config(config_file="configs\kubeconfig.yaml")
        self.apps_v1_api = client.AppsV1Api()
        self.core_v1_api = client.CoreV1Api()

    def getAllNamespaces(self):
        try:
            namespaces = self.core_v1_api.list_namespace()
            return [namespace.metadata.name for namespace in namespaces.items]
        except Exception as e:
            print(f"Error getting namespaces: {e}")
            return []

    def getAllDeployments(self, namespace="default"):
        try:
            deployments = self.apps_v1_api.list_namespaced_deployment(namespace=namespace)
            return deployments.items
        except Exception as e:
            print(f"Error getting deployments in namespace {namespace}: {e}")
            return []

    def getDeploymentReplicas(self, namespace, deployment_name):
        try:
            # 获取 Deployment 对象
            deployment = self.apps_v1_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
            # 获取副本数
            replica_count = deployment.spec.replicas
            return replica_count
        except Exception as e:
            print(f"Error getting Deployment replicas: {e}")
            return None

    def updateDeploymentReplicas(self, namespace, deployment_name, new_replica_count):
        try:
            # 获取 Deployment 对象
            deployment = self.apps_v1_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
            # 更新副本数
            deployment.spec.replicas = new_replica_count
            # 执行更新
            self.apps_v1_api.replace_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
            print(f"Deployment {deployment_name} in namespace {namespace} updated to {new_replica_count} replicas")
        except Exception as e:
            print(f"Error updating Deployment: {e}")


if __name__ == "__main__":
    kube_api_server = KubeApiServer()

    # 获取所有 Namespace
    all_namespaces = kube_api_server.getAllNamespaces()
    print("All Namespaces:", all_namespaces)

    # 获取默认 Namespace 下的所有 Deployment
    all_deployments = kube_api_server.getAllDeployments('openfaas-fn')
    # 打印每个 Deployment 的名称和副本数
    for deployment in all_deployments:
        print(f"Deployment Name: {deployment.metadata.name}, Replicas: {deployment.spec.replicas}")
