# Exercises part 1: Pods and Deployments

## Table of contents

- [Exercises part 1: Pods and Deployments](#exercises-part-1-pods-and-deployments)
  - [Table of contents](#table-of-contents)
  - [Prepare the Kubernetes environment](#prepare-the-kubernetes-environment)
  - [1. Create an image](#1-create-an-image)
  - [2. Kubernetes resource: Pod](#2-kubernetes-resource-pod)
    - [Basic Pod definition](#basic-pod-definition)
    - [Creating a Pod](#creating-a-pod)
    - [Listing resources](#listing-resources)
    - [Get the generated definition of the pod](#get-the-generated-definition-of-the-pod)
    - [Labeling a Kubernetes resource](#labeling-a-kubernetes-resource)
    - [Editing a Kubernetes resource](#editing-a-kubernetes-resource)
    - [Connecting to the application of the pod](#connecting-to-the-application-of-the-pod)
    - [A crashed pod](#a-crashed-pod)
      - [Troubleshooting](#troubleshooting)
  - [3. Kubernetes resource: Deployment](#3-kubernetes-resource-deployment)
    - [Basic Deployment definition](#basic-deployment-definition)
    - [Creating the application within a deployment](#creating-the-application-within-a-deployment)
    - [Scale the deployment](#scale-the-deployment)
    - [Editing the deployment](#editing-the-deployment)
    - [Crashing the application](#crashing-the-application)
  - [Bonus InitContainer](#bonus-initcontainer)

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

Docs: [kubernetes.io](https://k8s.io/docs/concepts/workloads/pods/)

A Pod is the smallest and simplest Kubernetes object. It represents a single instance of a running process in your cluster. Pods contain one or more containers.

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

### Labeling a Kubernetes resource

Labels are key-value pairs that are attached to objects, such as pods. They are used to organize and select subsets of objects. They are handy for you as a developer but is also used by Kubernetes to select objects.

add a label to the pod with the key `foo` and the value `bar`. You can use the `kubectl label` command to add a label to the pod.

Run the following command to check if the label has been added.

```shell
kubectl get pod/backend --selector=foo=bar
```


<details><summary>Spoiler!</summary>

```shell
kubectl label pod/backend foo=bar
```
</details>

### Editing a Kubernetes resource

When there is more to change, use the `kubectl edit` command.

With the `kubectl edit` command you can edit the definition of a resource. This can be useful when you want to change something in the pod definition. Note not all fields are changeable.

Use the kubectl edit command to edit the pod you've created earlier. Change the label foo=bar to bar=foo.

!NOTE `kubectl edit` will open the editor defined by your KUBE_EDITOR, or EDITOR environment variables, or fall back to 'vi' for Linux or 'notepad' for Windows. If you want to use a different editor you can set the environment variable.

Run the following command to check if the label has been changed.

```shell
kubectl get pod/backend --selector=bar=foo
```

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

To have a better understanding of what happened we can look at the logs of the pod.

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

Docs: [kubernetes.io](https://k8s.io/docs/concepts/workloads/controllers/deployment/)

The pod is a basic building block of Kubernetes. It is not recommended to use pods directly in a production environment. Since they are not very resilient and have little to no self-healing capabilities.

The best and most common way is to let a Kubernetes resource called a `Deployment` manage the pods.
With a deployment, you can specify how many replicas of a pod you want to run, update the specification of the pod, or even rollback to a previous version of the pods.

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

<details><summary>Spoiler!</summary>

```shell
kubectl scale deployment/backend --replicas=5
```

</details>

### Editing the deployment

Before we continue, we will setup some monitoring to visualize what happens. Use the following command to watch the pods.

```shell
kubectl get pods --selector=foo=baz --watch
```

The results will be empty since the pods are not (yet) labeled with `foo=baz`.

Since the deployment is managing the pods we can easily change the pods that are managed by the deployment. Use the `kubectl edit` command to add a label to the pod template. Add the label `foo=baz` to the pod template.

You should see all the pods that are managed by the deployment to update to fit the new pod template.

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
It would be nice to connect to the other pods of the deployment so that the application can be more resiliant en give the crashing pod time to restart. 
We will explore more in the next part with a resource called `Service`

## Bonus InitContainer

Docs: [kubernetes.io](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)

A pod can have multiple containers. One of the containers can be an `InitContainer`. An InitContainer is a container that runs before the application container starts. This can be useful for setting up the environment for the application container. or to wait for a service to be available.

Add an `InitContainer` to the pod definition of the deployment. The `InitContainer` should run a very important process with the following command command `echo "Hello from InitContainer && sleep 10"`.

<details><summary>Spoiler!</summary>

add the following to the pod template of the deployment.

```yaml
    ...
    spec:
      initContainers:
      - name: init
        image: busybox
        command: ['sh', '-c', 'echo "Hello from InitContainer && sleep 10"']
      containers:
        ...
```

</details>
If you want to clean up the namespace you can use the following command:

```shell
kubectl delete namespace kubernetes-ws-1
```
