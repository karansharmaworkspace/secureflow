# Phase 1 Plan: Infrastructure & Network Capture

**Goal:** Deploy base K8s cluster, Zeek passive sensor on SPAN/TAP port, and initial Kafka topic for `raw-api-calls`.

## Tasks

### 1.1 Provision K8s Cluster
- Deploy Kubernetes cluster (3+ nodes) for all platform workloads
- Configure namespace structure (`listen`, `remember`, `detect`, `enforce`, `act`)
- Set up RBAC, resource quotas, and network policies

### 1.2 Deploy Zeek on SPAN/TAP Port
- Identify core switch SPAN/TAP port configuration
- Deploy Zeek sensor node (bare-metal or VM, not containerized — requires raw NIC access)
- Configure Zeek to listen on the mirrored port
- Write Zeek HTTP log script to extract: path, method, status code, user-agent, timestamp, source IP, response size
- Verify Zeek does NOT capture payload content (metadata-only compliance)

### 1.3 Deploy Kafka Cluster
- Deploy Apache Kafka (3-broker cluster) on K8s using Strimzi operator
- Create topic `raw-api-calls` with appropriate partitioning (12 partitions, replication factor 3)
- Configure retention: 30 days for raw logs
- Set up Kafka ACLs for access control

### 1.4 Integrate Zeek → Kafka
- Configure Zeek Kafka plugin to stream JSON-formatted logs to `raw-api-calls` topic
- Verify end-to-end: HTTP request on mirrored port → Zeek capture → Kafka message
- Validate message schema: path, method, status_code, user_agent, timestamp, source_ip, response_size

### 1.5 Monitoring & Validation
- Deploy basic monitoring (Zeek health, Kafka broker health, topic throughput)
- Validate SPAN/TAP captures real traffic without packet loss
- Document network topology and data flow for compliance

## Success Criteria
1. K8s cluster operational with all namespaces provisioned
2. Zeek sensor deployed on SPAN/TAP port, capturing HTTP metadata
3. Kafka topic `raw-api-calls` receiving Zeek logs in real time
4. Verified: no payload content in captured logs
5. End-to-end latency < 500ms from HTTP request to Kafka message

## Dependencies
- Network team: SPAN/TAP port configuration on core switch
- Infrastructure team: Bare-metal VM or dedicated NIC for Zeek
- Security team: Approval for passive network monitoring

---
*Created: 2026-05-26*
