# Frontend Analyzer

Playwright-based static analysis tool that discovers API endpoints by analyzing JavaScript bundles at build time. Extracts API call patterns from frontend code to identify endpoints that might not be documented elsewhere.

## Files

### main.js
Playwright automation script that crawls the frontend application, captures network requests, and analyzes JavaScript bundles to discover embedded API endpoint references.

### package.json
Node.js package configuration with Playwright as the main dependency for browser automation.

### __tests__/
Test directory containing unit and integration tests for the analyzer.
