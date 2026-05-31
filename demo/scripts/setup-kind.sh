#!/bin/bash
set -euo pipefail

K8S_VERSION="${K8S_VERSION:-v1.29.2}"

echo "=== Creating kind cluster ==="
kind create cluster --config demo/kind-config.yaml --image "kindest/node:${K8S_VERSION}"

echo "=== Verifying cluster ==="
kubectl cluster-info --context kind-zombie-platform-demo
kubectl get nodes

echo "=== Installing MetalLB for LoadBalancer ==="
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml
kubectl wait --namespace metallb-system --for=condition=ready pod --selector=app=metallb --timeout=120s

SUBNET=$(docker network inspect kind -f '{{(index .IPAM.Config 0).Subnet}}' | cut -d. -f1,2)
cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: demo-pool
  namespace: metallb-system
spec:
  addresses:
  - ${SUBNET}.255.200-${SUBNET}.255.250
EOF

cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: demo-l2
  namespace: metallb-system
spec:
  ipAddressPools:
  - demo-pool
EOF

echo "=== kind cluster ready ==="
