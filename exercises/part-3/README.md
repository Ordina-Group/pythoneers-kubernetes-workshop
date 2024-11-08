# Exercises part 3: Statefulness and persistance

In this part we will iterate on the previous exercises and add statefulness and persistance to the application. We will use a database to store the data and make sure that the data is not lost when the application is redeployed.

## Table of contents

- [Exercises part 3: Statefulness and persistance](#exercises-part-3-statefulness-and-persistance)
  - [Table of contents](#table-of-contents)
  - [Prepare the Kubernetes environment](#prepare-the-kubernetes-environment)
  - [1. Prepare the starting point](#1-prepare-the-starting-point)
  - [2. Kubernetes resource: StatefulSet](#2-kubernetes-resource-statefulset)
    - [Basic StatefulSet definition](#basic-statefulset-definition)
    - [Create a statefulset for the database of the fastapi app](#create-a-statefulset-for-the-database-of-the-fastapi-app)
    - [Create a service for the statefulSet](#create-a-service-for-the-statefulset)
    - [Connecting the backend app to the database](#connecting-the-backend-app-to-the-database)
    - [A loss of data](#a-loss-of-data)
  - [3. Kubernetes resource: PersistentVolumeClaim](#3-kubernetes-resource-persistentvolumeclaim)
    - [A basic PersistentVolumeClaim definition](#a-basic-persistentvolumeclaim-definition)
    - [Creating a PersistentVolumeClaim](#creating-a-persistentvolumeclaim)
    - [Update the stateful set to use the PersistentVolumeClaim](#update-the-stateful-set-to-use-the-persistentvolumeclaim)
  - [Bonus: Kubernetes resource: NetworkPolicy](#bonus-kubernetes-resource-networkpolicy)
    - [A basic NetworkPolicy definition](#a-basic-networkpolicy-definition)
    - [Limiting traffic](#limiting-traffic)
  - [Cleanup](#cleanup)

## Prepare the Kubernetes environment

!NOTE Podman Desktop users to remove the ingress resource from the previous exercises, since it will conflict with the one we will add to the namespace of this exercise. To remove the ingress resource use the following command:

```shell
kubectl delete -f exercises/part-2/manifest-kind-ingress.yaml
```

Just like in the previous exercises we will create a new namespace to work in. This will prevent pods of different exercises from interfering with each other.

Use the following command to create a namespace named: `kubernetes-ws-3`

```shell
kubectl create namespace kubernetes-ws-3
```

Just like before, set the current context to the new namespace using the following command:

```shell
kubectl config set-context --current --namespace kubernetes-ws-3
```

## 1. Prepare the starting point

To iterate on the previous exercises we will start with the same starting point. Use the following command to create the starting point:

!NOTE Podman Desktop users need to change the image to `localhost/app:v1` in the manifest.yaml file.

```shell
kubectl apply -f exercises/part-3/manifest.yaml
```

!NOTE Podman Desktop users need a ingress resource to access the fastapi application. Use the following command to create the ingress resource:

```shell
kubectl apply -f exercises/part-3/manifest-kind-ingress.yaml
```

The fastapi application is now running in the `kubernetes-ws-3` namespace.
The fastapi application is for the docker desktop users accessible at `http://localhost:8001`. For the Podman desktop users, the application is accessible at `http://localhost:9090`.

## 2. Kubernetes resource: StatefulSet

Docs: [kubernetes.io](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)

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

### Create a statefulset for the database of the fastapi app

Create a stateful set for the database of the fastapi app. Use the following information to create the stateful set:

- image: `postgres:13.3`
- environment variables trough a configMap:
  - POSTGRES_USER: `postgres`
  - POSTGRES_PASSWORD: `password`
  - POSTGRES_DB: `database`
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

### Create a service for the statefulSet

Create a service for the statefulSet to make it accessible from the fastapi app. Since this service does not need to be accessible from outside the cluster use a `ClusterIP` service with the name `db-service`.

<details><summary>Spoiler!</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-service
spec:
  selector:
    app: db
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
```

</details>

### Connecting the backend app to the database

The backend deployment needs a revision to connect to the database. Add the environment variable `DATABASE_URL` to the backend deployment with the following pattern `postgresql://<POSTGRES_USER>:<POSTGRES_PASSWORD>@db-service:5432/<POSTGRES_DB>` fill in the correct values used in the statefulSet

When the backend deployment is updated the fastapi application should be able to connect to the database. Try to create a new item in the fastapi application to see if the connection is working.

### A loss of data

Simulating a server crash by deleting the pod the `statefulSet` has created by using the `kubectl delete pod` command. The `statefulSet` will create a new pod to replace the deleted pod.

Sadly the data that was stored in the database is lost. This is because the data is stored in the pod with the emptyDir volume and not in a persistent volume. To make sure the data is not lost when the pod is deleted we need to store the data in a persistent volume.

## 3. Kubernetes resource: PersistentVolumeClaim

Docs: [kubernetes.io](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)

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

create a `PersistentVolumeClaim` for the database, its been tested that the db works with a 10Mi volume.

Check with the following command if the `PersistentVolumeClaim` and the `PersistentVolume` are created:

```shell
kubectl get pvc,pv
```

### Update the stateful set to use the PersistentVolumeClaim

Earlier in this exercise we created a volume named `data` in the stateful set definition. This volume is already mounted to the container at the path `/var/lib/postgresql/data`. Update the stateful set to use the `PersistentVolumeClaim` you created earlier. Seek in the [Kubernetes documentation about storage](https://kubernetes.io/docs/concepts/storage/) how to configure the `PersistentVolumeClaim` as a volume in the statefulSet.

<details><summary>Tip 1</summary>

This is the chapter in the Kubernetes documentation that explains how to use a `PersistentVolumeClaim` as a volume in a pod:
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

## Bonus: Kubernetes resource: NetworkPolicy

Docs: [kubernetes.io](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

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

Create only the fastapi application is allowed to make inbound traffic to the database. The database should not be able to make outbound connections.

To ensure your network policy is working correctly connect the terminal of the database pod and try to connect to the fastapi application or any website with `ping`. The connection should be refused.

<details><summary>Tip 1: How to connect to the terminal of a pod</summary>

```shell
kubectl exec -it <statefulSet-name> -- sh
```

</details>

## Cleanup

If you want to clean up the namespace you can use the following command:

```shell
kubectl delete namespace kubernetes-ws-3
```
