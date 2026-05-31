#!/usr/bin/env python3
"""
SecureFlow Everywhere - Streamlit Dashboard

Two modes:
  Demo  - runs the synthetic traffic pipeline, displays results
  Real  - upload a codebase zip, scan for API routes, classify, score
"""

import io
import json
import os
import re
import sys
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
LOGO_PATH = SCRIPT_DIR / "logo.png"

# ---------------------------------------------------------------------------
# API route detection patterns
# ---------------------------------------------------------------------------
ROUTE_PATTERNS = {
    "python_flask": [
        re.compile(r'@(?:app|bp|blueprint)\.(route|get|post|put|delete|patch)\s*\(\s*[\'"](.+?)[\'"]'),
        re.compile(r'@(?:app|bp|blueprint)\.add_url_rule\s*\(\s*[\'"](.+?)[\'"]'),
    ],
    "python_fastapi": [
        re.compile(r'@(?:app|router)\.(get|post|put|delete|patch|api_view)\s*\(\s*[\'"](.+?)[\'"]'),
        re.compile(r'@app\.(add_api_route)\s*\(\s*[\'"](.+?)[\'"]'),
    ],
    "python_django": [
        re.compile(r'path\s*\(\s*[\'"](.+?)[\'"]'),
        re.compile(r'url\s*\(\s*r?[\'"](.+?)[\'"]'),
    ],
    "javascript_express": [
        re.compile(r'(?:app|router|server)\.(get|post|put|delete|patch|all)\s*\(\s*[\'`](.+?)[\'`]'),
    ],
    "javascript_nestjs": [
        re.compile(r'@(Get|Post|Put|Delete|Patch|All)\s*\(\s*[\'"](.+?)[\'"]'),
    ],
    "java_spring": [
        re.compile(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*\(\s*[\'"](.+?)[\'"]'),
    ],
    "go_gin": [
        re.compile(r'(?:r|group|router)\.(GET|POST|PUT|DELETE|PATCH|Any)\s*\(\s*[\'"](.+?)[\'"]'),
    ],
}

# Framework -> language mapping
FRAMEWORK_LANG = {
    "python_flask": "Python",
    "python_fastapi": "Python",
    "python_django": "Python",
    "javascript_express": "JavaScript",
    "javascript_nestjs": "TypeScript",
    "java_spring": "Java",
    "go_gin": "Go",
}

# Security heuristics: patterns that indicate good security practices
SECURITY_GOOD_PATTERNS = [
    (re.compile(r'(?:@login_required|@auth_required|@jwt_required|@requires_auth|@protected)', re.I), "Auth decorator"),
    (re.compile(r'(?:middleware|authenticate|authorize|verify_token|check_token)', re.I), "Auth middleware"),
    (re.compile(r'(?:rate.?limit|throttle|RateLimit)', re.I), "Rate limiting"),
    (re.compile(r'(?:validate|sanitiz|escap|xss|injection)', re.I), "Input validation"),
    (re.compile(r'(?:csrf|cors|helmet)', re.I), "CSRF/CORS protection"),
    (re.compile(r'(?:bcrypt|argon2|scrypt|pbkdf2|hash_password)', re.I), "Password hashing"),
    (re.compile(r'(?:TLS|HTTPS|ssl|secure)', re.I), "TLS/HTTPS"),
]

SECURITY_BAD_PATTERNS = [
    (re.compile(r'(?:eval\s*\(|exec\s*\(|os\.system\s*\(|subprocess\.call\s*\([^)]*shell\s*=\s*True)', re.I), "Code injection risk"),
    (re.compile(r'(?:SELECT.*FROM.*%s|INSERT.*INTO.*%s|execute\s*\([^)]*%s)', re.I), "SQL injection risk"),
    (re.compile(r'(?:password\s*=\s*[\'"][^\'"]+[\'"]|secret\s*=\s*[\'"][^\'"]+[\'"])', re.I), "Hardcoded credentials"),
    (re.compile(r'(?:debug\s*=\s*True|DEBUG\s*=\s*True)', re.I), "Debug mode enabled"),
    (re.compile(r'(?:no.?verify|verify\s*=\s*False|insecure)', re.I), "Disabled verification"),
]


# ---------------------------------------------------------------------------
# Code scanner for "Real" mode
# ---------------------------------------------------------------------------
def scan_codebase(upload_bytes: bytes) -> dict:
    """Extract zip, scan all source files for API routes, return structured results."""
    endpoints = []
    files_scanned = 0
    frameworks_found = set()

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(upload_bytes)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp)

        # Walk all files
        for root, _dirs, files in os.walk(tmp):
            for fname in files:
                fpath = os.path.join(root, fname)
                ext = Path(fname).suffix.lower()

                # Only scan source files
                if ext not in (".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php"):
                    continue

                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as sf:
                        content = sf.read()
                except Exception:
                    continue

                files_scanned += 1
                rel_path = os.path.relpath(fpath, tmp)

                for framework, patterns in ROUTE_PATTERNS.items():
                    for pat in patterns:
                        for match in pat.finditer(content):
                            groups = match.groups()
                            if len(groups) == 2:
                                method = groups[0].upper() if len(groups[0]) <= 6 else groups[0]
                                route = groups[1]
                            elif len(groups) == 1:
                                method = "ANY"
                                route = groups[0]
                            else:
                                continue

                            # Normalize method
                            method_map = {
                                "route": "ANY", "add_url_rule": "ANY", "api_view": "ANY",
                                "add_api_route": "ANY",
                            }
                            method = method_map.get(method.lower(), method.upper())

                            frameworks_found.add(framework)

                            # Security analysis for this file
                            good_hits = []
                            bad_hits = []
                            for pat, label in SECURITY_GOOD_PATTERNS:
                                if pat.search(content):
                                    good_hits.append(label)
                            for pat, label in SECURITY_BAD_PATTERNS:
                                if pat.search(content):
                                    bad_hits.append(label)

                            # Get relative file path within the project
                            # Strip the tmp directory prefix to get the original path
                            parts = rel_path.split(os.sep)
                            if len(parts) > 1:
                                project_path = os.sep.join(parts[1:])  # skip tmp dir name
                            else:
                                project_path = rel_path

                            endpoints.append({
                                "file": project_path,
                                "framework": framework,
                                "language": FRAMEWORK_LANG.get(framework, "Unknown"),
                                "method": method,
                                "route": route,
                                "line": content[:match.start()].count("\n") + 1,
                                "security_good": good_hits,
                                "security_bad": bad_hits,
                            })

    # Deduplicate by (route, method, framework)
    seen = set()
    unique = []
    for ep in endpoints:
        key = (ep["route"], ep["method"], ep["framework"])
        if key not in seen:
            seen.add(key)
            unique.append(ep)

    return {
        "files_scanned": files_scanned,
        "frameworks_found": sorted(frameworks_found),
        "total_routes": len(unique),
        "endpoints": unique,
    }


def score_code_endpoint(ep: dict) -> dict:
    """Score a scanned code endpoint for security posture."""
    good = len(set(ep.get("security_good", [])))
    bad = len(set(ep.get("security_bad", [])))
    total_patterns = good + bad

    # Base score from security practices found
    if total_patterns > 0:
        base = (good / total_patterns) * 70 + 30  # 30-100 range
    else:
        base = 50  # unknown = middle

    # Penalty for bad patterns
    penalty = bad * 12
    score = max(0, min(100, base - penalty))

    findings = []
    for label in ep.get("security_bad", []):
        findings.append(label)
    for label in ep.get("security_good", []):
        findings.append(f"[OK] {label}")

    if not ep.get("security_good"):
        findings.append("No security patterns detected in file")

    if score >= 80:
        risk = "low"
    elif score >= 60:
        risk = "medium"
    elif score >= 40:
        risk = "high"
    else:
        risk = "critical"

    return {
        "security_score": round(score, 1),
        "risk_level": risk,
        "findings": findings,
        "security_good_count": good,
        "security_bad_count": bad,
    }


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
def get_logo():
    if LOGO_PATH.exists():
        return str(LOGO_PATH)
    return None


def render_header():
    logo = get_logo()
    col1, col2 = st.columns([1, 5])
    with col1:
        if logo:
            st.image(logo, width=100)
        else:
            st.markdown("<div style='font-size:64px;text-align:center;line-height:100px;'>&#9760;</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("# SecureFlow Everywhere")
        st.markdown("*API Security Posture Scanner*")
    st.divider()


def render_demo_mode():
    st.header("Demo Mode")
    st.markdown("Run the synthetic traffic pipeline on 100K+ simulated banking API endpoints.")

    if st.button("Run Demo Pipeline", type="primary", key="run_demo"):
        with st.spinner("Generating synthetic traffic data ..."):
            import subprocess
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "demo" / "traffic-generator" / "simulate.py"), "--generate-features"],
                cwd=str(PROJECT_ROOT),
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                st.error(f"Data generation failed:\n{result.stderr[:500]}")
                return
            st.success("Synthetic data generated.")

        parquet = PROJECT_ROOT / "demo" / "test-data" / "endpoint_features.parquet"
        scan_json = PROJECT_ROOT / "demo" / "test-data" / "registry_scan.json"

        with st.spinner("Scanning registry and classifying endpoints ..."):
            # Import and run scanner directly
            sys.path.insert(0, str(SCRIPT_DIR))
            from registry_scanner import scan
            data = scan(str(parquet), str(scan_json))

        render_results(data)

    # Check if previous results exist
    scan_json = PROJECT_ROOT / "demo" / "test-data" / "registry_scan.json"
    if scan_json.exists():
        st.info("Previous scan results found. Click 'Run Demo Pipeline' to refresh, or view cached results below.")
        if st.button("Load Cached Results", key="load_cached"):
            with open(scan_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            render_results(data)


def render_real_mode():
    st.header("Real Mode")
    st.markdown("Upload your codebase as a `.zip` file. SecureFlow Everywhere will scan for API routes, classify them, and score security posture.")

    uploaded = st.file_uploader(
        "Upload codebase zip",
        type=["zip"],
        help="Contains your API source code (Python, JavaScript, TypeScript, Java, Go). Max 4 GB.",
        max_upload_size=4096,
    )

    if uploaded is not None:
        with st.spinner("Scanning codebase for API routes ..."):
            bytes_data = uploaded.read()
            result = scan_codebase(bytes_data)

        if result["total_routes"] == 0:
            st.warning("No API routes detected. Make sure your zip contains source files with route definitions (Flask, FastAPI, Express, Spring, etc.).")
            return

        st.success(f"Scanned {result['files_scanned']} files. Found {result['total_routes']} API routes across {len(result['frameworks_found'])} frameworks.")

        # Score each endpoint
        scored = []
        for ep in result["endpoints"]:
            scoring = score_code_endpoint(ep)
            scored.append({**ep, **scoring})

        # Sort by security score (lowest first = most at risk)
        scored.sort(key=lambda x: x["security_score"])

        # Build summary
        risk_counts = defaultdict(int)
        lang_counts = defaultdict(int)
        fw_counts = defaultdict(int)
        total_score = 0
        for ep in scored:
            risk_counts[ep["risk_level"]] += 1
            lang_counts[ep["language"]] += 1
            fw_counts[ep["framework"]] += 1
            total_score += ep["security_score"]

        avg_score = round(total_score / len(scored), 1) if scored else 0

        summary = {
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_endpoints": len(scored),
            "summary": {
                "active": len(scored),  # all discovered = "active" in code context
                "deprecated": 0,
                "orphaned": 0,
                "avg_security_score": avg_score,
                "total_annual_cost_inr": 0,
                "zombie_annual_cost_inr": 0,
            },
            "finding_counts": {},
            "endpoints": [
                {
                    "endpoint_key": f"{ep['framework']}|{ep['method']}|{ep['route']}",
                    "host": ep["file"],
                    "domain": ep["language"],
                    "api_version": 0,
                    "method": ep["method"],
                    "path": ep["route"],
                    "traffic_level": "unknown",
                    "classification": ep["risk_level"],
                    "security_score": ep["security_score"],
                    "is_zombie": 0,
                    "annual_cost_inr": 0,
                    "risk_level": ep["risk_level"],
                    "findings": ep["findings"],
                }
                for ep in scored
            ],
            "code_scan": {
                "files_scanned": result["files_scanned"],
                "frameworks_found": result["frameworks_found"],
                "language_breakdown": dict(lang_counts),
                "framework_breakdown": dict(fw_counts),
                "risk_breakdown": dict(risk_counts),
            },
        }

        # Collect finding counts
        for ep in scored:
            for f in ep["findings"]:
                summary["finding_counts"][f] = summary["finding_counts"].get(f, 0) + 1

        render_results(summary, code_mode=True)


def render_results(data: dict, code_mode: bool = False):
    s = data["summary"]
    total = data["total_endpoints"]

    # Summary cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Endpoints", f"{total:,}")
    c2.metric("Avg Security Score", f"{s['avg_security_score']}")
    if not code_mode:
        c3.metric("Active", f"{s['active']:,}")
        c4.metric("Deprecated", f"{s['deprecated']:,}")
    else:
        risk = data.get("code_scan", {}).get("risk_breakdown", {})
        c3.metric("Critical Risk", f"{risk.get('critical', 0)}")
        c4.metric("High Risk", f"{risk.get('high', 0)}")

    # Code scan details
    if code_mode and "code_scan" in data:
        cs = data["code_scan"]
        st.subheader("Codebase Overview")
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Files Scanned", cs["files_scanned"])
        cc2.metric("Frameworks Found", len(cs["frameworks_found"]))
        cc3.metric("Languages", len(cs["language_breakdown"]))

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Frameworks Detected**")
            for fw in cs["frameworks_found"]:
                st.markdown(f"  - {fw}")
        with col_b:
            st.markdown("**Language Breakdown**")
            for lang, count in sorted(cs["language_breakdown"].items(), key=lambda x: -x[1]):
                st.markdown(f"  - {lang}: {count} routes")

    # Cost analysis (demo mode only)
    if not code_mode and s.get("total_annual_cost_inr", 0) > 0:
        st.subheader("Cost Analysis")
        co1, co2, co3 = st.columns(3)
        co1.metric("Total Annual Cost", f"INR {s['total_annual_cost_inr']:,.0f}")
        co2.metric("Zombie Cost", f"INR {s['zombie_annual_cost_inr']:,.0f}")
        co3.metric("Potential Savings", f"INR {s['zombie_annual_cost_inr']:,.0f}/yr")

    # Classification distribution
    st.subheader("Classification Distribution")
    if not code_mode:
        dist_data = {
            "Active": s["active"],
            "Deprecated": s["deprecated"],
            "Orphaned": s["orphaned"],
        }
    else:
        dist_data = data.get("code_scan", {}).get("risk_breakdown", {})

    st.bar_chart(dist_data)

    # Security findings
    finding_counts = data.get("finding_counts", {})
    if finding_counts:
        st.subheader("Security Findings")
        sorted_findings = sorted(finding_counts.items(), key=lambda x: -x[1])
        for fname, count in sorted_findings[:15]:
            severity = "[CRITICAL]" if "injection" in fname.lower() or "credential" in fname.lower() else "[HIGH]" if "debug" in fname.lower() or "disabled" in fname.lower() else "[INFO]"
            st.markdown(f"**{severity}** {fname} -- **{count}** occurrences")

    # Endpoint table
    st.subheader("Endpoint Details")
    endpoints = data.get("endpoints", [])

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        risk_filter = st.multiselect(
            "Filter by risk level",
            ["low", "medium", "high", "critical"],
            default=["critical", "high"],
            key="risk_filter",
        )
    with fc2:
        if not code_mode:
            cls_filter = st.multiselect(
                "Filter by classification",
                ["active", "deprecated", "orphaned"],
                default=["deprecated", "orphaned"],
                key="cls_filter",
            )
        else:
            cls_filter = None
    with fc3:
        search = st.text_input("Search path / file", key="search_filter")

    filtered = endpoints
    if risk_filter:
        filtered = [ep for ep in filtered if ep["risk_level"] in risk_filter]
    if cls_filter and not code_mode:
        filtered = [ep for ep in filtered if ep["classification"] in cls_filter]
    if search:
        search_lower = search.lower()
        filtered = [ep for ep in filtered if search_lower in ep["path"].lower() or search_lower in ep.get("host", "").lower()]

    if filtered:
        st.markdown(f"**{len(filtered)} endpoints** matching filters")
        for ep in filtered[:200]:  # limit display
            risk_color = {"critical": "red", "high": "orange", "medium": "gold", "low": "green"}.get(ep["risk_level"], "gray")
            findings_text = " | ".join(ep["findings"][:3]) if ep["findings"] else "No findings"
            st.markdown(
                f":{risk_color}[**{ep['risk_level'].upper()}**] "
                f"`{ep['method']}` `{ep['path']}` "
                f"score={ep['security_score']} -- {findings_text}"
            )
    else:
        st.info("No endpoints match the current filters.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="SecureFlow Everywhere",
        page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
        layout="wide",
    )

    render_header()

    tab_demo, tab_real = st.tabs(["Demo Mode", "Real Mode"])

    with tab_demo:
        render_demo_mode()

    with tab_real:
        render_real_mode()


if __name__ == "__main__":
    main()
