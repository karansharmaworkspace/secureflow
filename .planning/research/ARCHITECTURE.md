# Architecture Research: Zombie API Platform

## Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  LISTEN Layer                                                │
│  ┌─────────┐  ┌───────────┐  ┌────────────┐                 │
│  │  Zeek   │→ │  Kafka    │→ │  Flink     │                 │
│  │ (SPAN)  │  │ (Streams) │  │ (Features) │                 │
│  └─────────┘  └───────────┘  └─────┬──────┘                 │
├────────────────────────────────────┼──────────────────────────┤
│  REMEMBER Layer                    │                          │
│  ┌──────────┐  ┌───────┐  ┌───────┴──────┐                  │
│  │  Feast   │  │ Redis │  │   MinIO      │                  │
│  │ (Store)  │  │(Cache)│  │  (Storage)   │                  │
│  └────┬─────┘  └───────┘  └──────────────┘                  │
├───────┼───────────────────────────────────────────────────────┤
│  DETECT Layer                         │                      │
│  ┌────┴────────┐  ┌────────┐  ┌───────┴──────┐              │
│  │  XGBoost    │  │  SHAP  │  │   MLflow     │              │
│  │(Classifier) │  │(Explain)│  │  (Tracking)  │              │
│  └─────┬───────┘  └────────┘  └──────────────┘              │
├───────┼───────────────────────────────────────────────────────┤
│  ENFORCE Layer                        │                      │
│  ┌────┴───────┐  ┌──────────┐  ┌──────┴──────┐              │
│  │  OPA       │  │  Kyverno │  │  Backstage  │              │
│  │ (Policy)   │  │(Admission)│  │ (Catalog)   │              │
│  └─────┬──────┘  └──────────┘  └─────────────┘              │
├───────┼───────────────────────────────────────────────────────┤
│  ACT Layer                            │                      │
│  ┌────┴────────┐  ┌────────────────┐                        │
│  │  GH Actions  │  │   Flagger      │                        │
│  │(Orchestrate) │  │  (Canary)      │                        │
│  └─────────────┘  └────────────────┘                        │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Discovery**: Zeek captures HTTP metadata from SPAN/TAP port mirror → Kafka topic (`raw-api-calls`)
2. **Feature Computation**: Flink consumes `raw-api-calls`, computes 20+ features per endpoint → writes to Feast + Redis
3. **Classification**: XGBoost reads features from Redis → classifies each endpoint → outputs zombie probability + SHAP explanation
4. **Policy Evaluation**: OPA evaluates decommission policies against classification + metadata → decision (approve/reject/escalate)
5. **Workflow**: GitHub Actions triggers decommission workflow → opens GitHub issue (Stage 2) or runs canary (Stage 3)
6. **Enforcement**: Kyverno intercepts new API deployments → verifies sunset-date and owner labels → rejects non-compliant

## Build Order Dependencies

1. Phase 1: Infrastructure (K8s, Kafka, MinIO) — foundation for everything
2. Phase 2: Listen Layer (Zeek, Flink) — must have data flowing
3. Phase 3: Remember Layer (Feast, Redis) — must store features
4. Phase 4: Detect Layer (XGBoost, SHAP, MLflow) — must classify
5. Phase 5: Enforce Layer (OPA, Kyverno, Backstage) — must have policies
6. Phase 6: Act Layer (GH Actions, Flagger) — must have decommission workflow
7. Phase 7: Discovery Methods 2-5 — layered on top of core pipeline
8. Phase 8: Compliance & Governance — charter, audit trail, documentation
