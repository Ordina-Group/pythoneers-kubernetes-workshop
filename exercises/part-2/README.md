# Exercises part 2: Services and ConfigMaps & Secrets

## Table of contents

- [Exercises part 2: Services and ConfigMaps \& Secrets](#exercises-part-2-services-and-configmaps--secrets)
  - [Table of contents](#table-of-contents)
  - [Prepare the Kubernetes environment](#prepare-the-kubernetes-environment)
  - [1. Kubernetes resource: Service](#1-kubernetes-resource-service)
    - [A basic service definition](#a-basic-service-definition)
    - [Creating a service](#creating-a-service)
    - [Crashing the application](#crashing-the-application)
  - [2. Environment variables with ConfigMaps and Secrets](#2-environment-variables-with-configmaps-and-secrets)
    - [`env` field](#env-field)
    - [ConfigMap](#configmap)
    - [Secret](#secret)
  - [Bonus: Canary deployment](#bonus-canary-deployment)
    - [Concept of a canary deployment](#concept-of-a-canary-deployment)
  - [Cleanup](#cleanup)
  - [Summary](#summary)

## Prepare the Kubernetes environment

Before starting the assignments, it is useful to create a `namespace`.
We won't delve too deeply into this for the workshop, but in short, it ensures that you have a
separate environment where you can `deploy` your Kubernetes resources for this part of
the workshop. A major advantage is that it is also easy to clean up!

Use the following command to create a namespace named: `kubernetes_ws_2`

```shell
kubectl create namespace kubernetes-ws-2
```

> namespace/kubernetes-ws-1 created

With the following command you can set the context of your kubectl to the just created namespace. This way you don't have to specify the namespace in every command.

```shell
kubectl config set-context --current --namespace kubernetes-ws-1
```

if you make use of the Kind cluster trough Podman Desktop, one more step is needed to have the same experience as with Docker Desktop.

```shell
kubectl apply -f exercises/part-1/manifest.yaml
```

This will make sure we can connect to the service we will create later on.

## 1. Kubernetes resource: Service

To be able to still interact with the application even when a single pod crashes we can use a Kubernetes resource called a `Service`.
With a service a connection can be made to a set of pods. This way we can make sure we have some kind of fallback mechanism.

### A basic service definition

```yaml
apiVersion: v1
kind: Service <- 1
metadata:
  name: app-service
spec:
  type: ClusterIP <- 2
  selector: <- 2
    app: backend <- 3
  ports:
    - targetPort: 80 <- 4
```

These are the key parts of the service definition:

1. The kind of resource we are creating is a `Service`
2. The `type` field specifies the type of service. In this case, it's a `ClusterIP` service. The other types are `NodePort`, `LoadBalancer`, and `ExternalName`.
3. The `selector` field is used to select the pods that the service should connect to.
4. The `targetPort` field specifies the port that the service should connect to on the pods.

### Creating a service

Just like with the deployment create a definition file to create a service named `backend-service` of type `LoadBalancer` that connects to the pods within the configured deployment.

<details><summary>Tip</summary>

If you forgot something you are able to edit the service with the following command:

```shell
kubectl edit service/backend-service
```

</details>

<details><summary>Spoiler</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: LoadBalancer
  selector:
    app: backend
  ports:
    - targetPort: 8000
```

```shell
kubectl create -f service.yaml
```

</details>

With the type LoadBalancer, the service will be exposed to the outside world. This way you can connect to the application without using the `port-forward` command.

With Docker Desktop the loadBalanced service is exposed to your localhost, visit the application here [http://localhost:8000]

With Podman Desktop the loadBalanced service is not automatically exposed, At the start we have created an ingress for you to connect to the service `backend-service`. Visit the application here [http://localhost:9090]

### Crashing the application

Let's crash the application for the last time.

Setup the `--watch` command to see the status of the pods.

```shell
kubectl get pods --watch
```

Crash the application by using the `/crash` endpoint.

This time you should only see the pods crashing and restarting. while the connection to the application is still available. This is because the service is connecting to the pods and not directly to a single pod. as its type suggests the service load balances the connection to the pods.


## 2. Environment variables with ConfigMaps and Secrets

There are multiple ways to set environment variables in a Kubernetes pod. One way is to set the environment variables in the container definition. Another way is to use a `ConfigMap` or a `Secret`. In this exercise we will explore the different ways to set environment variables in a pod and highlight the differences between them.

### `env` field

One way is to use the `env` field in the container definition.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    env:
    - name: FOO
      value: bar
```

### ConfigMap

A `ConfigMap` is a Kubernetes resource that is used to store configuration data. A `ConfigMap` can be used to store environment variables that are used by multiple pods.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  FOO: bar
```

To use all set environment variables in a `ConfigMap` in a pod you can use the `envFrom` field in the container definition.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod  
spec:
  containers:
  - name: my-container
    image: my-image
    envFrom:
    - configMapRef:
      name: my-config
```

### Secret

A `Secret` is a Kubernetes resource that is used to store sensitive data. A `Secret` can be used to store environment variables that are used by multiple pods. A `Secret` is similar to a `ConfigMap`, but the data in a `Secret` is stored in base64 encoded format.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
data:
  FOO: Rk9P
```

To use all set environment variables in a `Secret` in a pod you can use the `envFrom` field in the container definition.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod  
spec:
  containers:
  - name: my-container
    image: my-image
    envFrom:
    - configMapRef:
      name: my-secret
```

## Bonus: Canary deployment

With the 'guided' challenges above you should have a good understanding of some of the basic Kubernetes commands and resources. Which should give you the ability for the next more advanced challenge.

### Concept of a canary deployment

A canary deployment is used to test a new version of an application in a production environment. This new version is only a small number of pods that are running alongside the old version. This way the new version can be tested without affecting the whole application.

- Change something in the application and create a new image with the tag `app:v2`

**objective:** Create a canary deployment, with which your are able to reach the new version of the application and the old version of the application trough a single service.

<details><summary>Tip 1 </summary>
A canary deployment exists out of two deployments. One for the old version and one for the new version.
</details>
<details><summary>Tip 2 </summary>
Both deployments should have the same label so the service uses both deployments.
</details>
<details><summary>Solution!</summary>
Create a copy of the deployment with image `app:v1` and deploy it with the image `app:v2`. Make sure to change the name since there can't be multiple deployments with the same name. With only the image changed the service should be able to connect to both deployments since they have the same label.
</details>

## Cleanup

If you want to clean up the namespace you can use the following command:

```shell
kubectl delete namespace kubernetes-ws-2
```

!NOTE: For the Podman Desktop users, the ingress created at the start of the exercises must be removed before you can go to the next part of the workshop, since it will collide with the ingress of the next part of the workshop. if you do not want to clean up the namespace you can remove the ingress with the following command:

```shell
kubectl delete -f exercises/part-1/manifest.yaml
```

## Summary

<!-- #TODO: Create a small summery of the current extercises -->