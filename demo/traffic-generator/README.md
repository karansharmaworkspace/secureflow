# Traffic Generator

Generates realistic Union Bank-scale synthetic API traffic data for ML training.

## Files

| File | Purpose |
|------|---------|
| `simulate.py` | Main simulator. Generates 1,13,836 unique API endpoints across 17 banking domains (Accounts, UPI, NEFT, IMPS, RTGS, Cards, Loans, KYC, Forex, etc.). Computes 16 features per endpoint with heavily overlapping distributions between zombie and active classes. Outputs parquet file for ML training. Also supports live traffic mode (streams JSON to stdout). |
| `Dockerfile` | Container for running simulator as a Kubernetes pod or standalone. |

## Usage

```bash
# Generate feature dataset
python simulate.py --generate-features

# Live traffic mode (streams to stdout)
python simulate.py
```

## What It Models

- 17 banking domains with realistic endpoint counts
- Version drift (v1/v2/v3) with different zombie rates per version
- Traffic levels: critical (500K calls/day), high (100K), moderate (20K), low (2K), batch (500)
- 20+ user-agents (real browsers, mobile apps, monitoring tools)
- Annual cost estimation per endpoint (compute, storage, team, compliance, security risk)
