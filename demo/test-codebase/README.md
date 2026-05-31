# Test Codebase

Simulated banking API codebase used for testing the discovery and scanning components of the SecureFlow platform. Contains a realistic multi-language banking API with various endpoint types representing a production banking environment.

## Files

### test_scanner.py
Test script for the staging scanner component. Validates that the scanner correctly discovers endpoints in the test codebase.

### banking-api/
Mock banking API with implementations in four languages:
- Go: Handler-based API server
- Java: Spring-style API structure
- JavaScript: Express.js route definitions
- Python: Flask/FastAPI-style implementation
- Tests: Cross-language test suite

### banking-api.zip
Archived version of the banking API test codebase for portability.
