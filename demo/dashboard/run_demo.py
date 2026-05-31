#!/usr/bin/env python3
"""
SecureFlow Everywhere - Demo Runner

CLI entry point that chains the registry scanner and report generator,
then prints a terminal summary.
"""

import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))


def run_step(label, cmd, cwd=None):
    print(f"\n  {label}")
    result = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    [ERR] Failed: {' '.join(cmd)}")
        if result.stderr:
            for line in result.stderr.strip().splitlines()[:5]:
                print(f"      {line}")
        return False
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(f"    {line}")
    return True


def main():
    parser = argparse.ArgumentParser(description="SecureFlow Everywhere - Demo Runner")
    parser.add_argument("--parquet-path", default="demo/test-data/endpoint_features.parquet")
    parser.add_argument("--output-dir", default="demo/test-data")
    args = parser.parse_args()

    parquet = args.parquet_path
    out_dir = args.output_dir
    scan_json = os.path.join(out_dir, "registry_scan.json")
    report_html = os.path.join(out_dir, "registry_report.html")

    print("=" * 72)
    print("  SecureFlow Everywhere - API Registry Scan Demo")
    print("=" * 72)

    # Step 1: Check/generate feature data
    print("\n  [1/4] Checking for feature data ...")
    if not os.path.exists(parquet):
        print("    Not found. Generating synthetic data ...")
        ok = run_step(
            "Generating ...",
            [sys.executable, "demo/traffic-generator/simulate.py", "--generate-features"],
        )
        if not ok:
            print("\n  [ERR] Data generation failed. Aborting.")
            sys.exit(1)
    else:
        print(f"    Found: {parquet}")

    # Step 2: Run scanner
    ok = run_step(
        "[2/4] Scanning registry ...",
        [sys.executable, os.path.join(SCRIPT_DIR, "registry_scanner.py"),
         "--input", parquet, "--output", scan_json],
    )
    if not ok:
        print("\n  [ERR] Scanner failed. Aborting.")
        sys.exit(1)

    # Step 3: Generate report
    ok = run_step(
        "[3/4] Generating report ...",
        [sys.executable, os.path.join(SCRIPT_DIR, "report_generator.py"),
         "--input", scan_json, "--output", report_html],
    )
    if not ok:
        print("\n  [ERR] Report generation failed. Aborting.")
        sys.exit(1)

    # Step 4: Print summary from scan JSON
    import json
    with open(scan_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    s = data["summary"]
    total = data["total_endpoints"]
    findings = data.get("finding_counts", {})

    print("\n  [4/4] Summary")
    print()
    print("  " + "-" * 68)
    print("  CLASSIFICATION RESULTS")
    print("  " + "-" * 68)
    print(f"    Total endpoints:   {total}")
    print(f"    Active:            {s['active']}  ({s['active']/total*100:.1f}%)")
    print(f"    Deprecated:        {s['deprecated']}  ({s['deprecated']/total*100:.1f}%)")
    print(f"    Orphaned:          {s['orphaned']}  ({s['orphaned']/total*100:.1f}%)")
    print(f"    Avg Security Score: {s['avg_security_score']}")

    print()
    print("  " + "-" * 68)
    print("  TOP SECURITY FINDINGS")
    print("  " + "-" * 68)
    sorted_findings = sorted(findings.items(), key=lambda x: x[1], reverse=True)
    for fname, count in sorted_findings[:7]:
        severity = "[CRITICAL]" if count > total * 0.1 else "[HIGH]" if count > total * 0.05 else "[MEDIUM]"
        print(f"    {severity:12s} {count:>5d}  {fname}")

    print()
    print("  " + "-" * 68)
    print("  COST IMPACT")
    print("  " + "-" * 68)
    print(f"    Total Annual API Cost:  INR {s['total_annual_cost_inr']:>14,.0f}")
    print(f"    Zombie Endpoint Cost:   INR {s['zombie_annual_cost_inr']:>14,.0f}")
    print(f"    Potential Savings:      INR {s['zombie_annual_cost_inr']:>14,.0f} / year")

    print()
    print("  " + "-" * 68)
    print(f"  Report: {report_html}")
    print("  Open in browser to view the full dashboard.")
    print("  " + "-" * 68)
    print()


if __name__ == "__main__":
    main()
