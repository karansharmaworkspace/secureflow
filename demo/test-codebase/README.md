# Test Codebase

Simulated banking API codebase used for testing the discovery and scanning components of the SecureFlow platform. Contains a realistic multi-language banking API with various endpoint types representing a production banking environment, including legacy v1 endpoints that serve as zombie candidates.

## Files

### test_scanner.py — Scanner Validation Script (19 lines)

Imports `scan_codebase` and `score_code_endpoint` from `demo/dashboard/app.py` to test the static analysis pipeline. Reads `banking-api.zip`, runs the full scanner pipeline, and prints:
- Total files scanned
- Frameworks detected
- Total routes discovered
- Each zombie endpoint found (with framework, method, route path)

This validates that the frontend-analyzer regex patterns correctly detect routes across multiple languages and frameworks.

### banking-api/ — Multi-Language Mock Banking API

A simulated banking API with implementations in 4 languages, designed to test all 7+ framework regex patterns in the scanner. Contains both active endpoints and legacy v1 endpoints (zombie candidates).

Language implementations:
- **Go/:** Handler-based API server with Gin-like routing
- **Java/:** Spring-style API structure with controller annotations
- **JavaScript/:** Express.js route definitions
- **Python/:** Flask/FastAPI-style implementation with models, routes, and legacy v1 API

### banking-api.zip
Archived version of the banking API test codebase for portability and upload to the Streamlit dashboard's Real mode scanner.
