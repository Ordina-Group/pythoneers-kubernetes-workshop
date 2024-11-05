# Exercises part 2: Statefulness and persistance

In this part we will iterate on the previous exercises and add statefulness and persistance to the application. We will use a database to store the data and make sure that the data is not lost when the application is redeployed.

## Table of contents

- [Exercises part 2: Statefulness and persistance](#exercises-part-2-statefulness-and-persistance)
  - [Table of contents](#table-of-contents)
  - [Prepare the Kubernetes environment](#prepare-the-kubernetes-environment)
  - [1. Prepare the starting point](#1-prepare-the-starting-point)
  - [2. Kubernetes resource: StatefulSet](#2-kubernetes-resource-statefulset)
    - [Basic StatefulSet definition](#basic-statefulset-definition)
    - [Setting Environment Variables](#setting-environment-variables)
      - [`env` field](#env-field)
      - [ConfigMap](#configmap)
      - [Secret](#secret)
    - [Create a statefulset for the database of the fastapi app](#create-a-statefulset-for-the-database-of-the-fastapi-app)
    - [A loss of data](#a-loss-of-data)
  - [3. Kubernetes resource: PersistentVolumeClaim](#3-kubernetes-resource-persistentvolumeclaim)
    - [A basic PersistentVolumeClaim definition](#a-basic-persistentvolumeclaim-definition)
    - [Creating a PersistentVolumeClaim](#creating-a-persistentvolumeclaim)
    - [Update the stateful set to use the PersistentVolumeClaim](#update-the-stateful-set-to-use-the-persistentvolumeclaim)
  - [Bonus: Kubernetes resource: NetworkPolicy (docs)](#bonus-kubernetes-resource-networkpolicy-docs)
    - [A basic NetworkPolicy definition](#a-basic-networkpolicy-definition)
    - [Limiting traffic](#limiting-traffic)
    - [Seeing double](#seeing-double)
  - [Cleanup](#cleanup)
  - [Summary](#summary)

## Prepare the Kubernetes environment

Just like in the previous exercises we will create a new namespace to work in. This will prevent pods of different exercises from interfering with each other.

Use the following command to create a namespace named: `kubernetes_ws_2`

```shell
kubectl create namespace kubernetes-ws-2
```

Just like before, set the current context to the new namespace using the following command:

```shell
kubectl config set-context --current --namespace kubernetes-ws-2
```

## 1. Prepare the starting point

To iterate on the previous exercises we will start with the same starting point. Use the following command to create the starting point:

```shell
kubectl apply -f exercises/part-2/manifest.yaml
```

The fastapi application is now running in the `kubernetes-ws-2` namespace. You can access the application by port-forwarding the service to your local machine. just like before using the `port-forward` command

## 2. Kubernetes resource: StatefulSet

A Kubernetes `StatefulSet` is just like a `Deployment` a controller that manages a set of pods. The difference is that a `StatefulSet` is specifically designed for stateful applications. A stateful application is an application that stores data and has a unique identity. Examples of stateful applications are databases, message brokers, and key-value stores.

### Basic StatefulSet definition

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx # has to match .spec.template.metadata.labels
  serviceName: "nginx"
  replicas: 3 # by default is 1
  template:
    metadata:
      labels:
        app: nginx # has to match .spec.selector.matchLabels
    spec:
      containers:
      - name: nginx
        image: registry.k8s.io/nginx-slim:0.24
        ports:
        - containerPort: 80
          name: web
        volumeMounts: <- 1
        - name: www <- 2
          mountPath: /usr/share/nginx/html <- 3
  volumeClaimTemplates:
  - metadata:
      name: www <- 4
    spec:
      accessModes: [ "ReadWriteOnce" ] <- 5
      storageClassName: "my-storage-class" <- 6
      resources:
        requests:
          storage: 1Gi <- 7
```

1. The `volumeMounts` field is used to mount a volume to the container.
2. The `name` field is used to give the volume a name. This name is used in the `volumeClaimTemplates` field.
3. The `mountPath` field is used to specify the path in the container where the volume should be mounted.
4. The `volumeClaimTemplates` field is used to create a `PersistentVolumeClaim` for each pod in the `StatefulSet`.
5. The `accessModes` field is used to specify the access mode of the `PersistentVolumeClaim`. The access mode can be `ReadWriteOnce`, `ReadOnlyMany`, or `ReadWriteMany`.
6. The `storageClassName` field is used to specify the storage class of the `PersistentVolumeClaim`.
7. The `storage` field is used to specify the size of the `PersistentVolumeClaim`.

A VolumeClaimTemplate is an optional field in a StatefulSet definition which makes it easy to create a PersistentVolumeClaim for each pod in the StatefulSet. The PersistentVolumeClaim is automatically created when the StatefulSet is created.
For the following exercises we will created the PersistentVolumeClaim manually. but in a real-world scenario you would use the `volumeClaimTemplates` field to create the PersistentVolumeClaims automatically.

### Setting Environment Variables

To be able to connect to the database from the fastapi app some environment variables need to be set. There are a few ways to set environment variables in a Kubernetes pod. Trough the `env` field in the container definition, using a `ConfigMap`, or using a `Secret`. In this exercise your are free to choose which method you want to use. Note it increases the complexity of the exercise if you use a `ConfigMap` or `Secret`, if you want a challenge you can use these resources. If you want to keep it simple you can use the `env` field in the container definition.

#### `env` field

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

#### ConfigMap

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

#### Secret

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

### Create a statefulset for the database of the fastapi app

Create a stateful set for the database of the fastapi app. Use the following information to create the stateful set:
<!-- # TODO: check -->
- image: `postgres:13.3`
- environment variables:
  - user: `postgres`
  - password: `password`
  - database: `postgres`
- Mount a volume named `data` to the container at the path `/var/lib/postgresql/data`

Make use of the following template:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  <todo: fill in the metadata of the statefulset>
spec:
  selector:
    matchLabels:
      app: db 
  template:
    metadata:
      labels:
        app: db
    spec:
      volumes:
        - name: data
          emptyDir: 
      containers:
        <todo: fill in the container definition>
```

In the template above a volume named `data` is defined. This volume should be mounted to the container at the path `/var/lib/postgresql/data`.

After you have created the stateful set you can check if the stateful set is running by using the `kubectl get statefulset` command.

Check if you can connect to the database from the fastapi app. You can use the following command to port-forward the fastapi service to your local machine:

```shell
kubectl port-forward service/backend 8000:8000
```

Make use of the provided endpoints and try to add a new item to the database using the fastapi app. See if the item is added to the database if so the stateful set is working correctly.

### A loss of data

Simulating a server crash by deleting the pod the `statefulSet` has created by using the `kubectl delete pod` command. The `statefulSet` will create a new pod to replace the deleted pod.

Sadly the data that was stored in the database is lost. This is because the data is stored in the pod with the emptyDir volume and not in a persistent volume. To make sure the data is not lost when the pod is deleted we need to store the data in a persistent volume.

## 3. Kubernetes resource: PersistentVolumeClaim

A `PersistentVolumeClaim` is a Kubernetes resource that is a request for storage it is used to claim storage from the cluster. Which, when storage is available, is bound to a `PersistentVolume` by the cluster's storage provider. All data stored in a `PersistentVolume` is retained when the pod is deleted and is only deleted when the `PersistentVolume` resource is deleted.

### A basic PersistentVolumeClaim definition

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc 
spec:
  accessModes: <- 1
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi <- 2
```

1. The `accessModes` field is used to specify the access mode of the `PersistentVolumeClaim`. The access mode can be `ReadWriteOnce`, `ReadOnlyMany`, or `ReadWriteMany`. For most use cases `ReadWriteOnce` is sufficient.
2. The `storage` field is used to specify the size of the `PersistentVolumeClaim`. 

### Creating a PersistentVolumeClaim
<!-- #TODO: check -->
create a `PersistentVolumeClaim` for the database using the following information:

- At least use a minimum of ... of storage

### Update the stateful set to use the PersistentVolumeClaim

Earlier in this exercise we created a volume named `data` in the stateful set definition. This volume is already mounted to the container at the path `/var/lib/postgresql/data`. Update the stateful set to use the `PersistentVolumeClaim` you created earlier. Seek in the [Kubernetes documentation about storage](https://kubernetes.io/docs/concepts/storage/) how to configure the `PersistentVolumeClaim` as a volume in the statefulSet.

<details><summary>Tip 1</summary>

[Claims As Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#claims-as-volumes)

</details>

<details><summary>Tip 2</summary>

Instead of the following volume definition:

```yaml
volumes:
  - name: data
    emptyDir: 
```

Use the following volume definition:

```yaml
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: <todo: fill in the name of the PersistentVolumeClaim>
```

</details>




## Bonus: Kubernetes resource: NetworkPolicy [(docs)](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

A `NetworkPolicy` is comparable to firewall-rules in a traditional network.
Configuring a `NetworkPolicy` allows you to restrict the traffic to and from a pod.
By default, all traffic within a Kubernetes cluster is allowed.
Most cloud providers will already have default network policies in place that restrict the traffic.
But it is always a good practice to create your own network policies to restrict the traffic even further.
To restrict access to only those pods that need it.

### A basic NetworkPolicy definition

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: my-network-policy <- 1
spec:
  podSelector: <- 2
    matchLabels:
      app: backend
  policyTypes: <- 3
  - Ingress
  - Egress
  ingress:
  - from: <- 4
    - podSelector: <- 5
        matchLabels:
          app: backend
    ports: <- 6
    - protocol: TCP
      port: 80
  egress: <- 7
  - to:
    - namespaceSelector: <- 8
        matchLabels:
          kubernetes.io/metadata.name: kubernetes-ws-1
```

1. The name to give to the `NetworkPolicy`.
2. The `podSelector` field is used to select the pods to which the `NetworkPolicy` should be applied. if this field is left empty the `NetworkPolicy` will be applied to all pods in the namespace in which the `NetworkPolicy` is created.
3. Which types of policies are set. The `NetworkPolicy` can have the following types: `Ingress`, `Egress`, or both.
   - Egress (Outbound traffic): Restriction of traffic leaving the pod.
   - Ingress (Inbound traffic): Restriction of traffic entering the pod.
4. The `from` field is used to specify the traffic that is allowed to enter the pod. Multiple sources can be specified.
5. A `podSelector` can be used to select the pods that are allowed to enter the pod. In this example, only pods with the label `app: backend` are allowed to enter the pod.
6. `ports` can be specified to restrict the traffic to a specific port.
7. The `egress` field is used to specify the traffic that is allowed to leave the pod. Multiple destinations can be specified.
8. A `namespaceSelector` can be used to select the namespaces on attributes. In this example, traffic is allowed to leave the pod to pods in the namespace with the label `kubernetes.io/metadata.name: kubernetes-ws-1`.

Some basic examples are given within the [Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/). the following example shows how to create a `NetworkPolicy` to deny all in- and outbound traffic within the namespace:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### Limiting traffic

Create only the fastapi application is allowed to make inbound traffic to the database. The database should not be able to make outbound traffic to any other pod in the namespace.

To ensure your network policy is working correctly connect the terminal of the database pod and try to ping the fastapi pod. The ping should not be successful.

<details><summary>Tip 1: How to connect to the terminal of a pod</summary>

```shell
kubectl exec -it <statefulSet-name> -- sh
```

</details>

### Seeing double

Create a second deployment of both the fastapi application and the database in the same namespace. By creating a NetworkPolicy, Restrict the traffic between the two deployments. Each fastapi application should only be able to connect to its own database.

## Cleanup

If you want to clean up the namespace you can use the following command:

```shell
kubectl delete namespace kubernetes-ws-2
```

## Summary

<!-- #TODO: Create a small summery of the current exercises -->
