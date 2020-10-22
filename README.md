# simpleupdate

I couldn't find a way to make a simple POST request from Anywhere™ telling Kubernetes to either restart a rollout, or update only the deployment image tag.

So I've made one.

## API endpoints

### `/v0/<namespace>/<deployment>`

This endpoint mimics `kubectl rollout restart deployment`.

#### Usage

With namespace=web, deployment=app

```
curl -d "token" -X POST https://simpleupdate/v0/web/app
```

### `/v0/<namespace>/<deployment>/<tag>`

This endpoint patches the **first** container in the deployment to have the specified image tag.

This does not support changing the image name.

#### Usage

With namespace=web, deployment=app, tag=v2

```
curl -d "token" -X POST https://simpleupdate/v0/web/app/v2
```

## Deployment

Deployment is only supported through Kustomize.

Create these two files in your cluster's GitOps repo:

### `kustomization.yaml`
```
bases:
  - github.com/chauffer/simpleupdate/manifests?ref=master
namespace: simpleupdate

resources:
  - ingress.yaml  # bring your own ingress. namespace=simpleupdate service=simpleupdate

configMapGenerator:
  - name: simpleupdate-config
    namespace: simpleupdate
    files:
    - simpleupdate-config.yml
```

### `simpleupdate-config.yaml`

```
<bcrypt token> <namespace>/<deployment> [allowed_regex=.*]
<bcrypt token> <namespace>/<deployment> [allowed_regex=.*]
...
```

## Generating a Token

```
docker run --rm ghcr.io/chauffer/simpleupdate generate_token.py
# or with a custom length
docker run --rm -e LEN=48 ghcr.io/chauffer/simpleupdate generate_token.py
```
