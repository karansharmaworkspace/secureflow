# Zombie API Decommission Governance Charter

## 1. Purpose

This charter establishes the governance framework for the automated discovery, classification, and decommission of zombie API endpoints within Union Bank of India's infrastructure.

## 2. Scope

- **In-scope**: All HTTP/HTTPS API endpoints on the bank's internal network and exposed through WAF/API gateway
- **Out-of-scope**: TLS/mTLS encrypted service mesh traffic, external partner APIs not visible in logs, legacy non-HTTP protocols

## 3. Roles & Responsibilities

| Role | Responsible | Authority |
|------|-------------|-----------|
| **CIO** | Final approval authority for decommission policy | Sign charter, override exemption appeals |
| **CISO** | Security oversight, risk acceptance | Approve zombie classification methodology, sign charter |
| **Legal** | Regulatory compliance verification | Sign charter, verify RBI/GDPR/PCI-DSS adherence |
| **Platform Engineering** | System operation, ML model maintenance | Technical execution, no decommission authority |
| **API Owner** | Respond to zombie notifications, provide evidence | Confirm, dispute, or request exemption |

## 4. Decommission Policy

### 4.1 Classification Thresholds

| Condition | Action |
|-----------|--------|
| F1 >= 0.85, 100% synthetic, ensemble disagreement < 0.3 | Auto-qualify for decommission |
| F1 >= 0.85, ensemble disagreement >= 0.3 | Mandatory human review |
| F1 < 0.85 | No action, continue monitoring |

### 4.2 Approval Chain

1. ML model flags endpoint as zombie candidate
2. Stage 2: GitHub issue opened, API owner has 30 days to respond
3. If owner confirms OR 30 days lapse: escalates to Stage 3
4. Stage 3 requires two INDEPENDENT human approvals (must be different people)
5. Approved: 24h Flagger canary → 10-day slow drain → full decommission

### 4.3 Exemption Process

API owners may request exemption with documented business justification.
Exemptions are valid for 90 days and require CISO re-approval upon expiry.

## 5. Compliance Requirements

- **No PII**: Metadata-only capture, Zeek redacts card data at sensor level
- **Retention**: Raw logs 30 days, feature vectors 90 days, audit records permanent
- **Encryption**: AES-256 at rest for all stored data
- **Access Control**: Kafka ACLs, K8s RBAC, network policies
- **Audit Trail**: Every decommission produces immutable Git record with approver identities and timestamps

## 6. Acceptance

| Role | Name | Signature | Date |
|------|------|-----------|------|
| CIO | | | |
| CISO | | | |
| Legal | | | |

---
*Document version: 1.0*
*Created: 2026-05-26*
