# Staging Scanner

Kiterunner-style path scanner that probes staging environments for undocumented API endpoints. Used to discover forgotten or orphaned endpoints that still exist in staging but may no longer be actively maintained.

## Files

### scanner.sh
Shell script that performs path scanning using common API path patterns and wordlists. Tests for endpoint existence and captures response characteristics for classification.

### Dockerfile
Container build for the scanner, packaging it with required dependencies for Kubernetes or standalone deployment.
