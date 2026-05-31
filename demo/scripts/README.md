# Demo Scripts

Automation scripts for setting up the demo environment, generating synthetic test data, and deploying the SecureFlow platform.

## Files

### deploy-all.sh
Full platform deployment script that deploys all 8 phases of the infrastructure onto a kind Kubernetes cluster. Orchestrates the deployment order across all namespaces.

### generate-test-data.ps1
PowerShell script for generating synthetic test data. Creates realistic banking API traffic patterns and endpoint feature datasets for ML model training and validation.

### run-ml-demo.sh
End-to-end ML pipeline demo script. Runs feature generation, model training with MLflow tracking, and prediction with SHAP explanations in sequence.

### setup-kind.sh
Kind cluster setup script that creates a 3-node Kubernetes cluster with MetalLB load balancer support for local development and testing.

### verify.sh
Component health check script that validates all platform components are running correctly across all namespaces. Used after deployment to confirm operational status.
