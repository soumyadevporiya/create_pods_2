import urllib.request

from flask import jsonify
import json

import time

# Required for Kubernetes POD Management, ensure RBAC authorisation is configured
import os
import kubernetes
from kubernetes import client, config, watch
from kubernetes.client.models import V1PodSpec
from kubernetes.client.models import V1Container
from kubernetes.client.models import V1Pod
from kubernetes.client.models import V1ObjectMeta
from kubernetes.client import V1EnvVar

config.load_incluster_config()
v1 = kubernetes.client.CoreV1Api()

for i in range(5, 10):
    container_name = 'container-with-envs-{}'.format(i)
    namespace = 'default'
    pod_name = 'my-bq-read-pod-{}'.format(i)

    image = 'gcr.io/level-approach-382012/ns_monolith_parallel_reader_v2:latest'
    env1 = V1EnvVar(name='ITER', value=str(i))
    env2 = V1EnvVar(name='POD_TYPE', value='1st')
    env3 = V1EnvVar(name='PCT', value='1')
    container = V1Container(name=container_name, image=image, env=[env1, env2, env3])

    node_name = ''
    if i <= 6:
        node_name = 'gke-cluster-1-default-pool-308539de-30c4'
    elif i <= 8:
        node_name = 'gke-cluster-1-default-pool-308539de-4b5z'
    else:
        node_name = 'gke-cluster-1-default-pool-308539de-f1dc'

    podspec = V1PodSpec(containers=[container], restart_policy="Always", node_name=node_name)
    metadata = V1ObjectMeta(name=pod_name, namespace=namespace)
    pod = V1Pod(api_version='v1', kind='Pod', metadata=metadata, spec=podspec)

    my_pod = v1.create_namespaced_pod(namespace, pod)

    while True:
        resp = v1.read_namespaced_pod(name=pod_name, namespace='default')
        if resp.status.phase != 'Pending':
            break
        time.sleep(0.01)

    while True:
        resp = v1.read_namespaced_pod(name=pod_name, namespace='default')
        if resp.status.phase == 'Running':
            break
    print("Pod is created")
