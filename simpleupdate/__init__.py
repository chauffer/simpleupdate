from datetime import datetime

from addict import Dict
from flask import Flask, request

import kubernetes

from .authorize import Authorize
from .settings import SIMPLEUPDATE_CONFIG

app = Flask(__name__)
Auth = Authorize(SIMPLEUPDATE_CONFIG)

K8s = kubernetes.client.ApiClient(
    kubernetes.config.load_incluster_config()
)
AppsV1API = kubernetes.client.AppsV1Api(K8s)

@app.route("/")
def hello():
    return "<a href='https://github.com/sim1/simpleupdate'>simpleupdate</a>"

@app.route("/v0/<namespace>/<deployment>", methods=["POST"])
def update_inplace(namespace, deployment):
    token = list(request.form.keys())[0]
    if not Auth.is_authorized(token, namespace, deployment):
        return 'unauthorized', 401

    reset = Dict()
    reset.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = datetime.now().isoformat()
    try:
        AppsV1API.patch_namespaced_deployment(
            deployment, namespace, reset
        )
    except:
        return 'failed', 500
    return 'done', 200

@app.route("/v0/<namespace>/<deployment>/<tag>", methods=["POST"])
def update_tag(namespace, deployment, tag):
    token = list(request.form.keys())[0]
    if not Auth.is_authorized(token, namespace, deployment, tag):
        return 'unauthorized', 401

    k8s_dep = AppsV1API.read_namespaced_deployment(deployment, namespace)

    image = k8s_dep.spec.template.spec.containers[0].image.split(':')

    if len(image) == 1:
        image.append(tag)
    else:
        image[1] = tag
    candidate_image = ':'.join(image)

    patch = Dict()
    patch.spec.template.spec.containers = [{
        'image': candidate_image,
        'name': k8s_dep.spec.template.spec.containers[0].name,
    }]

    try:
        AppsV1API.patch_namespaced_deployment(
            deployment, namespace, patch
        )
    except:
        return 'failed', 500
    return 'done', 200


if __name__ == "__main__":
    app.run()
