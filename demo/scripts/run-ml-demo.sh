#!/bin/bash
set -euo pipefail

echo "=== ML Pipeline Demo ==="
echo ""

echo "--- Step 1: Generate feature data ---"
python demo/traffic-generator/simulate.py --generate-features
echo ""

echo "--- Step 2: Install ML dependencies ---"
pip install -q -r ml-pipeline/requirements.txt
echo ""

echo "--- Step 3: Start MLflow (local mode) ---"
mlflow server --host 0.0.0.0 --port 5000 &
MLFLOW_PID=$!
sleep 3
echo "MLflow running (PID: $MLFLOW_PID)"
echo ""

echo "--- Step 4: Train XGBoost model ---"
MLFLOW_TRACKING_URI=http://localhost:5000 \
MLFLOW_EXPERIMENT_NAME=zombie-classification \
DATA_PATH=demo/test-data/endpoint_features.parquet \
  python ml-pipeline/train.py
echo ""

echo "--- Step 5: Test prediction ---"
cat << 'EOF' > /tmp/test_features.json
[
  {"endpoint_key":"api.bank.example.com|GET|/api/v1/accounts/1234","total_calls":10000,"synthetic_calls":10000,"real_calls":0,"days_since_last_real_call":60,"unique_user_agents":1,"unique_source_ips":1,"auth_ratio":0.0,"ratio_2xx":1.0,"ratio_4xx":0.0,"ratio_5xx":0.0,"response_size_mean":256,"response_size_stddev":5,"interarrival_mean_ms":60000,"interarrival_stddev_ms":10,"unique_hours_of_day":1,"is_100pct_synthetic":true},
  {"endpoint_key":"api.bank.example.com|GET|/api/v3/accounts/5678/balance","total_calls":2500,"synthetic_calls":200,"real_calls":2300,"days_since_last_real_call":0,"unique_user_agents":12,"unique_source_ips":8,"auth_ratio":0.95,"ratio_2xx":0.92,"ratio_4xx":0.05,"ratio_5xx":0.03,"response_size_mean":1200,"response_size_stddev":150,"interarrival_mean_ms":5000,"interarrival_stddev_ms":2000,"unique_hours_of_day":14,"is_100pct_synthetic":false}
]
EOF

MODEL_URI=$(mlflow runs list --experiment-name zombie-classification --output-format json 2>/dev/null | python -c "import sys,json; runs=json.load(sys.stdin); print(f'runs:/{runs[0][\"run_id\"]}/model' if runs else 'models:/zombie-classifier/latest')" 2>/dev/null || echo "models:/zombie-classifier/latest")

MODEL_URI=$MODEL_URI python ml-pipeline/predict.py /tmp/test_features.json
echo ""

echo "--- Step 6: OPA policy evaluation ---"
python -c "
import json, requests

test_cases = [
    {'endpoint_key': 'v1|zombie', 'f1_score': 0.92, 'is_100pct_synthetic': True, 'ensemble_disagreement': 0.1},
    {'endpoint_key': 'v3|active', 'f1_score': 0.92, 'is_100pct_synthetic': False, 'ensemble_disagreement': 0.1},
    {'endpoint_key': 'disputed', 'f1_score': 0.92, 'is_100pct_synthetic': True, 'ensemble_disagreement': 0.4},
]

for case in test_cases:
    resp = requests.post('http://localhost:8181/v1/data/zombie/decommission' if False else 'http://localhost:8181/v1/data/zombie/decommission',
                         json={'input': {**case, 'timestamp': '2026-05-26T00:00:00Z'}},
                         timeout=5)
    result = resp.json().get('result', {})
    print(f\"Endpoint: {case['endpoint_key']}\")
    print(f\"  allow: {result.get('allow')}\")
    print(f\"  decision: {result.get('decommission_decision')}\")
    print(f\"  human_review: {result.get('require_human_review')}\")
    print()
"

echo ""
echo "=== ML Demo Complete ==="

kill $MLFLOW_PID 2>/dev/null || true
