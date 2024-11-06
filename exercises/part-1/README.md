# Exercises part 1: The Kubernetes basics

## Table of contents

- [Exercises part 1: The Kubernetes basics](#exercises-part-1-the-kubernetes-basics)
  - [Table of contents](#table-of-contents)
  - [Prepare the Kubernetes environment](#prepare-the-kubernetes-environment)
  - [1. Create an image](#1-create-an-image)
  - [2. Kubernetes resource: Pod](#2-kubernetes-resource-pod)
    - [Basic Pod definition](#basic-pod-definition)
    - [Creating a Pod](#creating-a-pod)
    - [Listing resources](#listing-resources)
    - [Get the generated definition of the pod](#get-the-generated-definition-of-the-pod)
    - [Editing a Kubernetes resource](#editing-a-kubernetes-resource)
    - [Connecting to the application of the pod](#connecting-to-the-application-of-the-pod)
    - [A crashed pod](#a-crashed-pod)
      - [Troubleshooting](#troubleshooting)
  - [3. Kubernetes resource: Deployment](#3-kubernetes-resource-deployment)
    - [Basic Deployment definition](#basic-deployment-definition)
    - [Creating the application within a deployment](#creating-the-application-within-a-deployment)
    - [Scale the deployment](#scale-the-deployment)
    - [Crashing the application](#crashing-the-application)
  - [4. Kubernetes resource: Service](#4-kubernetes-resource-service)
    - [A basic service definition](#a-basic-service-definition)
    - [Creating a service](#creating-a-service)
    - [Crashing the application](#crashing-the-application-1)
  - [Bonus: Canary deployment](#bonus-canary-deployment)
    - [Concept of a canary deployment](#concept-of-a-canary-deployment)
  - [Cleanup](#cleanup)
  - [Summary](#summary)

## Prepare the Kubernetes environment

Before starting the assignments, it is useful to create a `namespace`.
We won't delve too deeply into this for the workshop, but in short, it ensures that you have a
separate environment where you can `deploy` your Kubernetes resources for this part of
the workshop. A major advantage is that it is also easy to clean up!

Use the following command to create a namespace named: `kubernetes_ws_1`

```shell
kubectl create namespace kubernetes-ws-1
```

With the following command you can set the context of your kubectl to the just created namespace. This way you don't have to specify the namespace in every command.

```shell
kubectl config set-context --current --namespace kubernetes-ws-1
```

## 1. Create an image

For the various assignments, we will use local container images. Your task is to use the Dockerfile in the repository to create an image tagged `app:v1`. You can use `docker build` or `podman build` for this.

You can verify the image creation by listing all Docker/podman images on your system.

```shell
docker images
```

or

```shell
podman images
```

<details> <summary>Spoiler! </summary> 

```shell
docker build . --tag app:v1 
```

or

```shell
podman build . --tag app:v1 
```


</details>

With podman desktop you will need to push the image to the Kind Cluster. Go to images tab -> locate the image you've build -> triple dots / hamburger menu -> "Push image to Kind cluster"
![image](https://github.com/user-attachments/assets/8d4f29de-8c6e-4518-9966-8bb274c42fdc)


## 2. Kubernetes resource: Pod

A Pod is the smallest and simplest Kubernetes object. It represents a single instance of a running process in your cluster. Pods contain one or more containers, such as Docker containers.

### Basic Pod definition

```yaml
apiVersion: v1 <- 1
kind: Pod <- 2
metadata:
  name: app <- 3
spec:
  containers: <- 4
    - name: app <- 5
      image: app:v1 <- 6
      ports:
        - containerPort: 8000 <- 7
```

These are the key parts of the pod definition:

1. `apiVersion`: Specifies the version of the Kubernetes API you’re using. For Pods, it’s typically v1.
1. `kind`: Defines the type of Kubernetes resource. Here, it’s Pod.
1. `metadata`: Contains metadata about the Pod, such as its name and labels.
1. `spec`: The specification of the desired state of the Pod.
1. `containers`: An array of containers that will run in the Pod. Each container has its own configuration.
1. `image`: Specifies the container image to use. In this example, it’s app:v1.
1. `ports`: Defines the ports that the container will expose. Here, port 8000 is exposed.

### Creating a Pod

There are a few ways of creating a pod. One of the fastest ways is using the command `kubectl run` make use of this command to create a pod with the image you created earlier (`app:v1`).

<details>

<summary>Tip 1 </summary>

Don't forget to use the commandline argument `--port` to expose the port opened by the application.

</details>
<details>

<summary>Spoiler! </summary>

```shell
kubectl run backend --image app:v1 --port 8000
```

</details>

### Listing resources

To see the resources you've created you can use the following command:

```shell
kubectl get pods
```

ps. this command can be used to list all kinds of resources in a Kubernetes namespace.

### Get the generated definition of the pod

Instead of creating a pod definition yourself, we've let Kubernetes generate one for you by using the `kubectl run` command.
To get the full definitie Kubernetes made for you can perform the following command:

```shell
kubectl get pod/backend --output yaml
```

### Editing a Kubernetes resource

With the `kubectl edit` command you can edit the definition of a resource. This can be useful when you want to change something in the pod definition. Note not all fields are changeable.

Use the kubectl edit command to edit the pod you've created earlier. add a label to the pod with the key `foo` and the value `bar`.

<details><summary>Spoiler!</summary>

```shell
kubectl edit pod/backend
```

Labels can be added to the metadata field of the pod definition.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: backend
  labels:
    foo: bar
...
```

</details>

### Connecting to the application of the pod

The application is running in the created pod. We yet haven't exposed the application to the outside world. By using
the `port-forward` command we can port the application to our local machine. So it is possible to interact with the application.

```shell
kubectl port-forward pod/backend 8000:8000
```

A timeout is added to the command to make sure the connection is closed when the pod is not running anymore.

Note: usually the Kubernetes cluster is running in a separate environment and exposing an application to the outside world could be a security risk. By using the `port-forward` command you can troubleshoot and test the application without any hassle.

### A crashed pod

To have a better understanding of how Kubernetes handles crashed pods we will crash the application.

To be able to see what is happening with the pod we will use the `get` command with the `--watch` flag.
keep a close eye on the pod status while crashing the application.

```shell
kubectl get pods --watch
```

Navigate to the swagger ui of the application [localhost:8000/api-docs](localhost:8000/api-docs)

There are a few endpoints created within the fastapi application.
Crash the application by using the `/crash` endpoint.

By crashing the application within the pod the following should happen:

- The pod status changed from `Running` to `Completed` to running again `Running`.
- The port-forward connection can be lost, when request were made to the application while it was crashed.

The pod has been restarted by Kubernetes. This is because the pod has crashed and Kubernetes has a self-healing mechanism that restarts the pod when it crashes.

#### Troubleshooting

The have a better understanding of what happend we can look at the logs of the pod.

```shell
kubectl logs pod/backend
```

As expected the `/crash` endpoint has crashed the application. and the pod has been restarted by Kubernetes.

There has also have been some events created by the pod. To see these events you can use the following command:

```shell
kubectl describe pod/backend
```

You should see three events when the application has crashed. A `Pulled` event, a `Created` event, and a `Started` event.

## 3. Kubernetes resource: Deployment

The pod is a basic building block of Kubernetes. It is not recommended to use pods directly in a production environment. Since they are not very resilient and have little to no self-healing capabilities.

The best and most common way is to let a Kubernetes resource called a `Deployment` manage the pods.
With a deployment, you can specify how many replicas of a pod you want to run, update the specification of the pod, or even rollback to a previous version of the pods.

<!-- #TODO: add graphics -->

### Basic Deployment definition

```yaml
apiVersion: apps/v1
kind: Deployment <- 1
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector: <- 2 # has to match .spec.template.metadata.labels
    matchLabels: <- 3
      app: nginx <- 4
  template: <- 5
    metadata:
      labels:
        app: nginx <- 6 # has to match .spec.selector.matchLabels
    spec:
      containers:
        - name: nginx
          image: nginx:1.14.2
          ports:
            - containerPort: 80
```

The following are the parts that we need to focus on:

1. The kind of resource we are creating is a `Deployment`
2. The `selector` field is used to select the pods that are managed by this deployment.
3. The `matchLabels` field is used is used that the deployment should select pods on the specified labels.
4. The `app: nginx` label is used to select the pods that are managed by this deployment.
5. The `template` field is used to specify the pod template this is very similar to the pod definition we've created earlier.
6. The `app: nginx` label is used to label the pods that are created by this deployment.
   Note: the labels in the `selector` and `template` fields are the same. This is important since this is what the
   the deployment uses to select the pods that it should manage.

### Creating the application within a deployment

To create a deployment we are not able to use the `kubectl run` command.
Instead, we will use the `kubectl create` command. Create a definition file to create a deployment named `app` with the image `app:v1` and `3` replicas.

<details><summary>Template</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  selector: <Use the correct selector>
  replicas: <replicas>
  template:
    metadata: <Pod metadata>
    spec: <Pod specification>
```

</details>

<details><summary>Tip 1 </summary>

For the pod specification, you can use look at the definition of the pod that you created earlier.
[Get the generated definition of the pod](#get-the-generated-definition-of-the-pod)

</details>

<details><summary>Spoiler! </summary>

<!-- # TODO: check the full definition of the deployment -->

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: app
          image: app:v1
          ports:
            - containerPort: 8000
```

</details>

### Scale the deployment

A major advantage of using a deployment is that you can easily scale the number of replicas of the pod. Make use of the `kubectl scale` command to scale your deployment to `5` replicas.

<details><summary>Spoiler! </summary>

```shell
kubectl scale deployment/backend --replicas=5
```

</details>

### Crashing the application

Now that the application is running within a deployment we can crash the application again.
just like before use the `port-forward` command to connect to the application.

<details><summary>Spoiler! </summary>

```shell
kubectl port-forward deployment/app 8000:8000 --pod-running-timeout 1s
```

</details>

Setup the `--watch` command to see the status of the pods.

```shell
kubectl get pods --watch
```

Crash the application by using the `/crash` endpoint.

This time still only the pod we are port-forwarded to should crash. The other pods should still be running, since no /crash endpoint is called on them.
But we would like to have a more resilient application. To make sure the application is still available when a pod crashes we can use a Kubernetes resource called a `Service`.

## 4. Kubernetes resource: Service

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
kubectl delete namespace kubernetes-ws-1
```

## Summary

<!-- #TODO: Create a small summery of the current extercises -->
