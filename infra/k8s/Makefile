.PHONY: all namespaces strimzi kafka zeek flink-operator flink topics minio redis feast mlflow opa kyverno backstage flagger network verify

all: namespaces strimzi kafka zeek flink-operator flink topics minio redis feast mlflow opa kyverno backstage flagger network verify

namespaces:
	kubectl apply -f namespaces.yaml

strimzi:
	kubectl apply -f kafka/strimzi-operator.yaml
	kubectl wait --for=condition=Ready pods -l name=strimzi-operator -n kafka --timeout=120s

kafka:
	kubectl apply -f kafka/kafka-cluster.yaml
	kubectl wait --for=condition=Ready kafka/kafka-cluster -n listen --timeout=300s
	kubectl apply -f kafka/kafka-acls.yaml

zeek:
	kubectl apply -f ../zeek/zeek-daemonset.yaml -n listen
	kubectl rollout status daemonset/zeek-sensor -n listen --timeout=120s

network:
	kubectl apply -f network-policies.yaml

rbac:
	kubectl apply -f rbac.yaml

flink-operator:
	kubectl apply -f flink/flink-operator.yaml
	kubectl wait --for=condition=Ready pods -l app.kubernetes.io/name=flink-kubernetes-operator -n flink --timeout=120s

flink:
	kubectl apply -f flink/flink-deployment.yaml
	kubectl wait --for=condition=Ready deployment/feature-computation-job -n listen --timeout=180s

topics:
	kubectl apply -f flink/kafka-topics.yaml

minio:
	kubectl apply -f minio/minio-deployment.yaml
	kubectl rollout status deployment/minio -n remember --timeout=120s
	kubectl apply -f minio/minio-buckets.yaml
	kubectl wait --for=condition=Complete job/minio-create-buckets -n remember --timeout=60s

redis:
	kubectl apply -f redis/redis-sentinel.yaml
	kubectl rollout status statefulset/redis -n remember --timeout=180s

feast:
	kubectl apply -f feast/feast-deployment.yaml
	kubectl rollout status deployment/feast-serving -n remember --timeout=120s

mlflow:
	kubectl apply -f mlflow/mlflow-deployment.yaml
	kubectl rollout status deployment/mlflow -n detect --timeout=120s

opa:
	kubectl apply -f opa/opa-deployment.yaml
	kubectl rollout status deployment/opa -n enforce --timeout=120s

kyverno:
	kubectl apply -f kyverno/kyverno-install.yaml
	kubectl wait --for=condition=Ready pods -n kyverno -l app.kubernetes.io/name=kyverno --timeout=180s
	kubectl apply -f kyverno/kyverno-policies.yaml

backstage:
	kubectl apply -f backstage/backstage-deployment.yaml
	kubectl rollout status deployment/backstage -n enforce --timeout=180s

flagger:
	kubectl apply -f flagger/flagger-install.yaml
	kubectl wait --for=condition=Ready pods -n flagger -l app=flagger --timeout=120s

verify:
	@echo "=== Checking namespaces ==="
	kubectl get namespaces -l layer
	@echo "=== Checking Kafka cluster ==="
	kubectl get kafka -n listen
	@echo "=== Checking Zeek DaemonSet ==="
	kubectl get daemonset zeek-sensor -n listen
	@echo "=== Checking topic ==="
	kubectl get kafkatopic raw-api-calls -n listen

clean:
	kubectl delete -f flagger/flagger-install.yaml --ignore-not-found
	kubectl delete -f backstage/backstage-deployment.yaml --ignore-not-found
	kubectl delete -f kyverno/kyverno-policies.yaml --ignore-not-found
	kubectl delete -f kyverno/kyverno-install.yaml --ignore-not-found
	kubectl delete -f opa/opa-deployment.yaml --ignore-not-found
	kubectl delete -f mlflow/mlflow-deployment.yaml --ignore-not-found
	kubectl delete -f feast/feast-deployment.yaml --ignore-not-found
	kubectl delete -f redis/redis-sentinel.yaml --ignore-not-found
	kubectl delete -f minio/minio-deployment.yaml --ignore-not-found
	kubectl delete -f minio/minio-buckets.yaml --ignore-not-found
	kubectl delete -f flink/flink-deployment.yaml --ignore-not-found
	kubectl delete -f flink/flink-operator.yaml --ignore-not-found
	kubectl delete -f ../zeek/zeek-daemonset.yaml --ignore-not-found
	kubectl delete -f kafka/kafka-cluster.yaml --ignore-not-found
	kubectl delete -f kafka/strimzi-operator.yaml --ignore-not-found
	kubectl delete -f namespaces.yaml --ignore-not-found
