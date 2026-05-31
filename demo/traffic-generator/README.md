# Traffic Generator

Banking API traffic simulation component that generates realistic, Union Bank-scale synthetic API traffic data for ML model training and validation. Produces a feature dataset with approximately 1,13,836 endpoints across 17 banking domains.

## Files

### simulate.py — Union Bank-Scale Traffic Simulator (941 lines)

**Architecture:** Uses a `DomainConfig` dataclass pattern to define per-domain behavior. Each domain specifies traffic_level (critical/high/moderate/low/batch), version range, endpoint path templates, and zombie rates per version.

**Entry Points:**
- `--generate-features` — Generates parquet feature file at `demo/test-data/endpoint_features.parquet`
- No args — Runs live traffic simulation mode (streams JSON to stdout)

**17 Banking Domains with Zombie Rates:**

| Domain | Host | Traffic | Zombie v1/v2/v3 | 
|--------|------|---------|-----------------|
| Accounts | api.bank.example.com | critical | 40%/20%/8% |
| UPI | upi.bank.example.com | critical | 35%/18%/6% |
| NEFT | neft.bank.example.com | high | 40%/22%/10% |
| IMPS | imps.bank.example.com | high | 38%/20%/9% |
| RTGS | rtgs.bank.example.com | high | 40%/22%/10% |
| Cards | cards.bank.example.com | high | 45%/25%/12% |
| Loans | loans.bank.example.com | moderate | 45%/28%/15% |
| KYC | kyc.bank.example.com | moderate | 35%/20%/8% |
| Forex | forex.bank.example.com | moderate | 42%/25%/12% |
| FixedDeposits | fd.bank.example.com | moderate | 40%/24%/10% |
| RecurringDeposits | rd.bank.example.com | moderate | 42%/26%/12% |
| Cheque | cheque.bank.example.com | low | 50%/30% (v1/v2) |
| Notifications | notify.bank.example.com | low | 45%/28%/15% |
| Admin | admin.bank.example.com | batch | 55%/35% (v1/v2) |
| Reporting | reporting.bank.example.com | low | 50%/32%/18% |
| AuthGateway | auth.bank.example.com | critical | 20%/10%/5% |
| FraudDetection | fraud.bank.example.com | critical | 25%/12%/6% |

**Key Design Rationale:**
- Older versions (v1) have zombie rates up to 55% to simulate version drift — endpoints get forgotten as newer API versions are deployed
- Critical domains (AuthGateway, FraudDetection) have lower zombie rates (5-20%) since they receive more security attention and active monitoring
- "Batch" domains (Admin) have highest zombie rates (55%) because they're called infrequently and easily forgotten
- Zombie rate multiplier adjusts per-domain: Admin=1.2x, Loans=1.1x, Cheque=1.1x, Reporting=1.1x

**Feature Generation (30 columns per endpoint):**
- `endpoint_key` — Unique identifier: `host|method|path`
- `total_calls` — Generated based on traffic_level distribution with poisson/normal noise
- `synthetic_calls` — Derived from zombie probability
- `real_calls` — `total_calls - synthetic_calls`
- `days_since_last_real_call` — High for zombies (up to 365), low for active (0-7)
- `unique_user_agents` — Zombies get 1-2, active get 5-20
- `unique_source_ips` — Zombies get 1-2, active get 8-30+
- `auth_ratio` — Zombies get 0.0-0.2, active get 0.7-1.0
- `ratio_2xx/4xx/5xx` — Status distribution (zombies have more 404/500 patterns)
- `response_size_mean/stddev` — Zombies have low stddev (automated polling)
- `interarrival_mean_ms/stddev_ms` — Bot traffic has regular intervals (low stddev)
- `unique_hours_of_day` — Bots hit 1-2 hours, real users spread across 8-16 hours
- `is_100pct_synthetic` — Flag for zero real traffic
- `is_zombie` — Ground truth label
- Domain metadata: domain, api_version, host, method, path, annual_cost_inr

**Overlapping Distributions:** Feature distributions between zombie and active classes are deliberately overlapping (not cleanly separable). This forces the ML model (XGBoost) to learn multi-feature interactions rather than relying on a single threshold — making the classification task genuinely challenging and realistic.

### Dockerfile
Multi-stage container build using `python:3.11-slim`. Installs dependencies (pandas, pyarrow, numpy) and packages simulate.py for deployment as a Kubernetes job or standalone container.
