# Streamlit Dashboard

Interactive web UI for SecureFlow with Demo and Real modes.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application. Demo mode runs synthetic pipeline on 1,13,836 endpoints. Real mode accepts codebase zip upload, scans for API routes, detects zombies, scores security posture. Uses plotly for interactive charts. Session state persists data across filter interactions. |
| `registry_scanner.py` | Scans parquet feature data. Classifies endpoints as active/deprecated/orphaned. Computes 0-100 security score based on auth ratio, UA diversity, IP diversity, error rates, recency, synthetic traffic. Outputs JSON. |
| `report_generator.py` | Reads scanner JSON output. Generates self-contained HTML dashboard with CSS-only pie chart, domain breakdown table, color-coded endpoint table, findings bar chart. Dark theme. |
| `run_demo.py` | CLI entry point. Chains scanner + report generator. Prints terminal summary with classification counts, findings, and cost impact. |

## Running

```bash
# Streamlit (local)
streamlit run demo/dashboard/app.py

# CLI demo
python demo/dashboard/run_demo.py
```

## Charts (Plotly)

- Classification distribution (donut chart)
- Risk distribution (horizontal bar)
- Security findings (horizontal bar with color-coded severity)
- Framework breakdown (bar chart, Real mode)
- Language breakdown (donut chart, Real mode)
- Score distribution (histogram)
