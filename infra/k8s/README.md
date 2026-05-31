# Kubernetes Infrastructure

Root directory for Kubernetes manifests organized by the five-layer platform architecture. Each component is deployed in its own namespace with network policies and RBAC controls.

## Directory Structure

### listen/ (Network Capture Layer)
- kafka/ - Strimzi Kafka operator with 3-broker cluster and ACLs
- flink/ - Apache Flink operator and feature computation deployment

### remember/ (Data Storage Layer)
- minio/ - S3-compatible object storage
- redis/ - Redis Sentinel 3-node HA cluster
- feast/ - Feast feature store

### detect/ (ML Classification Layer)
- mlflow/ - MLflow tracking server and model registry

### enforce/ (Policy and Governance Layer)
- opa/ - Open Policy Agent policy engine
- kyverno/ - Kyverno admission controller and policies
- backstage/ - Backstage developer portal

### act/ (Decommission Layer)
- flagger/ - Flagger canary deployment controller

## Supporting Files

### namespaces.yaml
Namespace definitions: listen, remember, detect, enforce, flagger

### network-policies.yaml
Network segmentation policies controlling inter-component traffic

### rbac.yaml
Role-based access control definitions for cross-namespace permissions

### Makefile
Make targets for deploying individual components or the full stack
