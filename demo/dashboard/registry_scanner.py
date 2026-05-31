#!/usr/bin/env python3
"""
SecureFlow Everywhere - API Registry Scanner

Scans the simulated API registry (parquet), classifies each endpoint as
active/deprecated/orphaned, and computes a security posture score (0-100).
Outputs structured JSON for the dashboard report generator.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def classify_endpoint(row):
    """
    Classify an endpoint into one of three categories:
      - active:     zombie=0, real traffic, recent activity
      - deprecated: zombie=1 OR low traffic with stale activity
      - orphaned:   zombie=1, zero real calls, long stale
    """
    is_zombie = int(row.get("is_zombie", 0))
    real_calls = float(row.get("real_calls", 0))
    days_stale = float(row.get("days_since_last_real_call", 0))

    if is_zombie == 1 and real_calls == 0 and days_stale > 90:
        return "orphaned"
    if is_zombie == 1 or (real_calls <= 100 and days_stale > 30 and days_stale <= 90):
        return "deprecated"
    return "active"


def compute_security_score(row):
    """
    Compute a 0-100 security posture score.
    Higher is better (more secure, healthier endpoint).
    """
    auth = float(row.get("auth_ratio", 0))
    ua = float(row.get("unique_user_agents", 0))
    ips = float(row.get("unique_source_ips", 0))
    r4xx = float(row.get("ratio_4xx", 0))
    r5xx = float(row.get("ratio_5xx", 0))
    days = float(row.get("days_since_last_real_call", 0))
    is_synth = int(row.get("is_100pct_synthetic", 0))

    score = 0.0
    score += min(auth, 1.0) * 25                        # auth coverage (max 25)
    score += min(ua / 10.0, 1.0) * 15                    # UA diversity (max 15)
    score += min(ips / 8.0, 1.0) * 15                    # IP diversity (max 15)
    score += max(0, 1.0 - r4xx - r5xx) * 20              # low error rate (max 20)
    score += max(0, 1.0 - days / 90.0) * 15              # recency (max 15)
    score += (1 - is_synth) * 10                          # not synthetic (max 10)

    return round(min(score, 100.0), 2)


def risk_level(score):
    if score >= 80:
        return "low"
    if score >= 60:
        return "medium"
    if score >= 40:
        return "high"
    return "critical"


def find_issues(row):
    findings = []
    if float(row.get("auth_ratio", 0)) < 0.3:
        findings.append("Low authentication coverage")
    if int(row.get("unique_user_agents", 0)) <= 2:
        findings.append("Minimal user-agent diversity")
    if int(row.get("unique_source_ips", 0)) <= 2:
        findings.append("Minimal source IP diversity")
    if float(row.get("ratio_4xx", 0)) + float(row.get("ratio_5xx", 0)) > 0.1:
        findings.append("High error rate (4xx+5xx > 10%)")
    if float(row.get("days_since_last_real_call", 0)) > 60:
        findings.append("No recent real traffic (>60 days)")
    if int(row.get("is_100pct_synthetic", 0)) == 1:
        findings.append("100% synthetic traffic")
    if int(row.get("is_zombie", 0)) == 1:
        findings.append("Classified as zombie endpoint")
    return findings


def scan(input_path, output_path):
    try:
        import pandas as pd
    except ImportError:
        print("[ERR] pandas is required. pip install pandas pyarrow", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(input_path):
        print(f"[ERR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"  Reading {input_path} ...")
    df = pd.read_parquet(input_path)
    total = len(df)
    print(f"  Loaded {total} endpoints")

    endpoints = []
    class_counts = {"active": 0, "deprecated": 0, "orphaned": 0}
    finding_counts = {}
    total_cost = 0.0
    zombie_cost = 0.0
    score_sum = 0.0

    for _, row in df.iterrows():
        classification = classify_endpoint(row)
        score = compute_security_score(row)
        risk = risk_level(score)
        issues = find_issues(row)
        annual_cost = float(row.get("annual_cost_inr", 0))
        is_zombie = int(row.get("is_zombie", 0))

        class_counts[classification] += 1
        score_sum += score
        total_cost += annual_cost
        if is_zombie:
            zombie_cost += annual_cost

        for f in issues:
            finding_counts[f] = finding_counts.get(f, 0) + 1

        endpoints.append({
            "endpoint_key": str(row.get("endpoint_key", "")),
            "host": str(row.get("host", "")),
            "domain": str(row.get("domain", "")),
            "api_version": int(row.get("api_version", 0)),
            "method": str(row.get("method", "")),
            "path": str(row.get("path", "")),
            "traffic_level": str(row.get("traffic_level", "")),
            "classification": classification,
            "security_score": score,
            "is_zombie": is_zombie,
            "annual_cost_inr": round(annual_cost, 2),
            "risk_level": risk,
            "findings": issues,
        })

    avg_score = round(score_sum / total, 2) if total > 0 else 0

    result = {
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_endpoints": total,
        "summary": {
            "active": class_counts["active"],
            "deprecated": class_counts["deprecated"],
            "orphaned": class_counts["orphaned"],
            "avg_security_score": avg_score,
            "total_annual_cost_inr": round(total_cost, 2),
            "zombie_annual_cost_inr": round(zombie_cost, 2),
        },
        "finding_counts": finding_counts,
        "endpoints": endpoints,
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print()
    print(f"  Scan complete: {total} endpoints")
    print(f"    Active:     {class_counts['active']}")
    print(f"    Deprecated: {class_counts['deprecated']}")
    print(f"    Orphaned:   {class_counts['orphaned']}")
    print(f"    Avg Score:  {avg_score}")
    print(f"  Output: {output_path}")

    return result


def main():
    parser = argparse.ArgumentParser(description="SecureFlow Everywhere - API Registry Scanner")
    parser.add_argument("--input", default="demo/test-data/endpoint_features.parquet",
                        help="Path to parquet feature file")
    parser.add_argument("--output", default="demo/test-data/registry_scan.json",
                        help="Path to output JSON")
    args = parser.parse_args()
    scan(args.input, args.output)


if __name__ == "__main__":
    main()
