# Pythoneers Kubernetes Workshop

This workshop is designed to give you a basic understanding of Kubernetes and how to deploy a simple python application using Kubernetes. 

## Table of Contents

- [Pythoneers Kubernetes Workshop](#pythoneers-kubernetes-workshop)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
    - [Kubernetes CLI](#kubernetes-cli)
    - [A Kubernetes Cluster](#a-kubernetes-cluster)
      - [Create a Kubernetes cluster using Docker Desktop](#create-a-kubernetes-cluster-using-docker-desktop)
      - [Create a Kubernetes cluster using Podman Desktop (Kind)](#create-a-kubernetes-cluster-using-podman-desktop-kind)
    - [Verify your setup](#verify-your-setup)


## Prerequisites

There are some prerequisites that you need to have installed on your machine before you can start with the workshop.

1. The Kubernetes CLI (`kubectl`)
1. A Kubernetes Cluster (Docker Desktop or Podman Desktop (Kind))


### Kubernetes CLI

To install the Kubernetes CLI, follow the instructions on the official Kubernetes documentation: [https://kubernetes.io/docs/tasks/tools/#kubectl]

### A Kubernetes Cluster

Choose one of the following options to create a Kubernetes cluster on your machine:

#### Create a Kubernetes cluster using Docker Desktop

- Download Docker desktop: https://www.docker.com/products/docker-desktop/
- In the Docker Desktop settings, go to the Kubernetes tab
![image](https://github.com/user-attachments/assets/97f36d02-b930-408f-9bf9-11ad0e8f3c50)
- Check the box to enable Kubernetes and click the "Apply & Restart" button in the bottom right corner
![image](https://github.com/user-attachments/assets/48824f7f-4d3b-4b0e-b684-b4e006d57ae1)

#### Create a Kubernetes cluster using Podman Desktop (Kind)

- Download Podman desktop: [https://podman-desktop.io/]
- Open Podman Desktop and download Podman in the dashboard and make sure it is running:
- Next, download the Kind CLI [https://kind.sigs.k8s.io/docs/user/quick-start/#installation]
- Thereafter, go to the settings in Podman Desktop and create a new kind cluster
- Now click on "create" to create a cluster

### Verify your setup

You should be able to run the following commands in your terminal:

```shell
kubectl version
```

```shell
docker version
```

or

```shell
podman version
```

Check if you have a running Kubernetes cluster running the following command:

```shell
kubectl get nodes
```

A node called `docker-desktop` or `kind-control-plane` should be listed or similar.

