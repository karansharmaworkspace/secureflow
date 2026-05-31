Write-Host "=== Generating ML Test Data ===" -ForegroundColor Cyan

Write-Host "Creating output directory..." -ForegroundColor Yellow
$null = New-Item -ItemType Directory -Path "demo/test-data" -Force

Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install pandas pyarrow numpy -q

Write-Host "Generating feature data for 200 endpoints..." -ForegroundColor Yellow
python demo/traffic-generator/simulate.py --generate-features

Write-Host "Verifying..." -ForegroundColor Yellow
python -c "import pandas as pd; df = pd.read_parquet('demo/test-data/endpoint_features.parquet'); print(f'Shape: {df.shape[0]} rows x {df.shape[1]} columns')"

Write-Host "=== Done ===" -ForegroundColor Green
