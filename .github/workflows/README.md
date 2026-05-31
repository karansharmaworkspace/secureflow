# GitHub Actions - Three-Stage Decommission Workflows

This directory contains the CI/CD workflows that implement the progressive three-stage decommission process for zombie API endpoints.

## Files

### stage1-watch-only.yml
Daily classification report workflow. Runs ML classification on all discovered endpoints and generates a report. No automated actions are taken at this stage - purely observational. Exit criteria: F1 >= 0.85.

### stage2-tell-owner.yml
Opens a GitHub issue for each zombie candidate detected. The issue includes SHAP explanations showing why the endpoint was classified as a zombie, plus evidence data. A 30-day response window is provided for the endpoint owner to confirm (zombie), dispute (with evidence), or request an exemption.

### stage3-turn-it-off.yml
Executes the actual decommission process when a zombie is confirmed:
1. 24-hour canary deployment at 1% traffic
2. 10-day slow drain period
3. Full endpoint removal
Safety gates require 2 human approvers, automatic rollback on anomaly detection, and full audit trail generation.
