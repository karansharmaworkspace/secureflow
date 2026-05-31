#!/usr/bin/env python3
"""
SecureFlow - Streamlit Dashboard

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
LOGO_PATH = PROJECT_ROOT / "logo.jpeg"

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

# Zombie API detection patterns - endpoints that are likely dead/abandoned
ZOMBIE_INDICATORS = [
    (re.compile(r'(?:deprecated|DEPRECATED|@deprecated|@Deprecated)', re.I), "Marked as deprecated"),
    (re.compile(r'(?:legacy|LEGACY|old_|_old)', re.I), "Legacy/old naming pattern"),
    (re.compile(r'(?:v1|v2)\b.*(?:deprecated|legacy|old)', re.I), "Old version with deprecation"),
    (re.compile(r'(?:temp|temporary|tmp|hack|fixme|todo|workaround)', re.I), "Temporary/hack code"),
    (re.compile(r'(?:unused|dead|remove|delete_me|to_delete)', re.I), "Explicitly marked for removal"),
    (re.compile(r'(?:mock|stub|fake|sample|example|test_|_test)', re.I), "Test/mock endpoint"),
    (re.compile(r'(?:debug|dev|development|staging)', re.I), "Debug/development endpoint"),
    (re.compile(r'(?:health|ping|alive|status|version)', re.I), "Health check (possible synthetic)"),
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
    """Score a scanned code endpoint for security posture. Returns score, risk, zombie status, and findings."""
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
    zombie_score = 0
    zombie_reasons = []

    # Check for zombie indicators
    route = ep.get("route", "")
    file_path = ep.get("file", "")
    full_context = f"{route} {file_path}"

    for pat, label in ZOMBIE_INDICATORS:
        if pat.search(full_context):
            zombie_score += 1
            zombie_reasons.append(label)
            findings.append(f"[ZOMBIE] {label}")

    # Additional zombie heuristics
    if route in ("/health", "/ping", "/alive", "/status", "/version", "/"):
        zombie_score += 1
        zombie_reasons.append("Generic health/status endpoint")

    if ep.get("method") == "ANY" and not any(m in route.lower() for m in ["get", "post", "put", "delete"]):
        zombie_score += 0.5

    for label in ep.get("security_bad", []):
        findings.append(f"[RISK] {label}")
    for label in ep.get("security_good", []):
        findings.append(f"[OK] {label}")

    if not ep.get("security_good"):
        findings.append("[WARN] No security patterns detected in file")

    is_zombie = zombie_score >= 2
    classification = "zombie" if is_zombie else "active"

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
        "classification": classification,
        "is_zombie": is_zombie,
        "zombie_reasons": zombie_reasons,
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


CUSTOM_CSS = """
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 32px; font-size: 15px; font-weight: 600;
        border-bottom: 3px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: #e94560; color: #fff;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
        border: 1px solid #0f3460; border-radius: 12px;
        padding: 20px 24px; min-height: 100px;
    }
    div[data-testid="stMetric"] label { color: #8899aa; font-size: 13px; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff; font-size: 28px; font-weight: 700; }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] { font-size: 13px; }
    .hero-box {
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 12px;
        padding: 40px; margin-bottom: 24px; text-align: center;
    }
    .hero-box h1 { color: #fff; font-size: 42px; margin: 0; font-weight: 800; letter-spacing: -1px; }
    .hero-box p { color: #8899aa; font-size: 16px; margin-top: 8px; }
    .section-card {
        background: #16213e; border: 1px solid #0f3460; border-radius: 12px;
        padding: 24px; margin-bottom: 20px;
    }
    .section-card h3 { color: #fff; font-size: 16px; margin: 0 0 16px 0; font-weight: 600; }
    .zombie-badge {
        display: inline-block; background: #e94560; color: #fff;
        padding: 2px 10px; border-radius: 6px; font-size: 11px;
        font-weight: 700; letter-spacing: 0.5px; margin-right: 8px;
    }
    .risk-low { background: #53d769; }
    .risk-medium { background: #ffcc00; color: #1a1a2e; }
    .risk-high { background: #ff8c00; }
    .risk-critical { background: #e94560; }
    .risk-badge {
        display: inline-block; padding: 2px 10px; border-radius: 6px;
        font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
    }
    .endpoint-row {
        background: #0f1a30; border: 1px solid #1a2a4a; border-radius: 8px;
        padding: 12px 16px; margin-bottom: 8px; font-size: 13px;
    }
    .endpoint-row:hover { border-color: #0f3460; }
    .ep-method { font-weight: 700; margin-right: 8px; }
    .ep-path { font-family: 'Cascadia Code', monospace; color: #ccc; }
    .ep-score { float: right; font-weight: 700; }
    .ep-findings { color: #8899aa; font-size: 12px; margin-top: 6px; }
    .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    .filter-bar { background: #0f1a30; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
    .upload-zone {
        border: 2px dashed #0f3460; border-radius: 16px; padding: 60px 40px;
        text-align: center; background: #0f1a30;
    }
    .upload-zone h3 { color: #fff; margin: 0 0 8px 0; }
    .upload-zone p { color: #8899aa; margin: 0; }
</style>
"""


def render_header():
    logo = get_logo()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="hero-box">
            <div style="display:flex;align-items:center;justify-content:center;gap:24px;">
                {"<img src='data:image/jpeg;base64," + __import__('base64').b64encode(open(logo, 'rb').read()).decode() + "' width='120' style='border-radius:16px;'>" if logo else "<div style='font-size:80px;line-height:120px;'>&#9760;</div>"}
                <div style="text-align:left;">
                    <h1>SecureFlow</h1>
                    <p>API Security Posture Scanner</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_demo_mode():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("<h3>Demo Mode</h3>", unsafe_allow_html=True)
    st.markdown("Run the synthetic traffic pipeline on 100K+ simulated banking API endpoints across 17 domains.")

    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        run_btn = st.button("Run Pipeline", type="primary", key="run_demo", use_container_width=True)
    with col2:
        cached_btn = st.button("Load Cached", key="load_cached", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    data = None

    if run_btn:
        with st.spinner("Generating synthetic traffic data ..."):
            import subprocess
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "demo" / "traffic-generator" / "simulate.py"), "--generate-features"],
                cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                st.error(f"Data generation failed:\n{result.stderr[:500]}")
                return
        with st.spinner("Scanning registry ..."):
            sys.path.insert(0, str(SCRIPT_DIR))
            from registry_scanner import scan
            data = scan(
                str(PROJECT_ROOT / "demo" / "test-data" / "endpoint_features.parquet"),
                str(PROJECT_ROOT / "demo" / "test-data" / "registry_scan.json"),
            )

    if cached_btn:
        scan_json = PROJECT_ROOT / "demo" / "test-data" / "registry_scan.json"
        if scan_json.exists():
            with open(scan_json, "r", encoding="utf-8") as f:
                data = json.load(f)

    if data:
        render_results(data)


def render_real_mode():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("<h3>Real Mode</h3>", unsafe_allow_html=True)
    st.markdown("Upload your codebase `.zip`. SecureFlow scans for API routes, identifies zombie APIs, and scores security posture.")
    st.markdown("</div>", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload codebase zip",
        type=["zip"],
        label_visibility="collapsed",
        help="Python, JavaScript, TypeScript, Java, Go. Max 4 GB.",
        max_upload_size=4096,
    )

    if uploaded is None:
        st.markdown(
            '<div class="upload-zone"><h3>Drop your codebase here</h3>'
            '<p>Supports Flask, FastAPI, Express, NestJS, Spring Boot, Gin and more</p></div>',
            unsafe_allow_html=True,
        )
        return

    with st.spinner("Scanning codebase ..."):
        result = scan_codebase(uploaded.read())

    if result["total_routes"] == 0:
        st.warning("No API routes detected.")
        return

    scored = [{**ep, **score_code_endpoint(ep)} for ep in result["endpoints"]]
    scored.sort(key=lambda x: (not x["is_zombie"], x["security_score"]))

    zombie_count = sum(1 for ep in scored if ep["is_zombie"])
    total = len(scored)
    avg_score = round(sum(ep["security_score"] for ep in scored) / total, 1) if total else 0

    risk_counts = defaultdict(int)
    lang_counts = defaultdict(int)
    fw_counts = defaultdict(int)
    for ep in scored:
        risk_counts[ep["risk_level"]] += 1
        lang_counts[ep["language"]] += 1
        fw_counts[ep["framework"]] += 1

    finding_counts = defaultdict(int)
    for ep in scored:
        for f in ep["findings"]:
            finding_counts[f] += 1

    summary = {
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_endpoints": total,
        "summary": {"active": total - zombie_count, "deprecated": 0, "orphaned": zombie_count, "avg_security_score": avg_score, "total_annual_cost_inr": 0, "zombie_annual_cost_inr": 0},
        "finding_counts": dict(finding_counts),
        "endpoints": [
            {
                "endpoint_key": f"{ep['framework']}|{ep['method']}|{ep['route']}",
                "host": ep["file"], "domain": ep["language"], "api_version": 0,
                "method": ep["method"], "path": ep["route"], "traffic_level": "unknown",
                "classification": "zombie" if ep["is_zombie"] else "active",
                "security_score": ep["security_score"], "is_zombie": 1 if ep["is_zombie"] else 0,
                "annual_cost_inr": 0, "risk_level": ep["risk_level"], "findings": ep["findings"],
            }
            for ep in scored
        ],
        "code_scan": {
            "files_scanned": result["files_scanned"],
            "frameworks_found": result["frameworks_found"],
            "language_breakdown": dict(lang_counts),
            "framework_breakdown": dict(fw_counts),
            "risk_breakdown": dict(risk_counts),
            "zombie_count": zombie_count,
        },
    }
    render_results(summary, code_mode=True)


def render_results(data: dict, code_mode: bool = False):
    s = data["summary"]
    total = data["total_endpoints"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Endpoints", f"{total:,}")
    c2.metric("Avg Score", f"{s['avg_security_score']}")
    if code_mode:
        zc = data.get("code_scan", {}).get("zombie_count", 0)
        c3.metric("Zombie APIs", f"{zc}", delta=f"{zc/total*100:.1f}%" if total else "0%", delta_color="inverse")
        c4.metric("Clean APIs", f"{total - zc}")
    else:
        c3.metric("Active", f"{s['active']:,}")
        c4.metric("Deprecated", f"{s['deprecated']:,}")

    if not code_mode and s.get("total_annual_cost_inr", 0) > 0:
        st.markdown('<div class="section-card"><h3>Cost Impact</h3></div>', unsafe_allow_html=True)
        co1, co2, co3 = st.columns(3)
        co1.metric("Total Annual", f"INR {s['total_annual_cost_inr']:,.0f}")
        co2.metric("Zombie Cost", f"INR {s['zombie_annual_cost_inr']:,.0f}")
        co3.metric("Savings", f"INR {s['zombie_annual_cost_inr']:,.0f}/yr")

    if code_mode and "code_scan" in data:
        cs = data["code_scan"]
        st.markdown('<div class="section-card"><h3>Codebase Overview</h3></div>', unsafe_allow_html=True)
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("Files", cs["files_scanned"])
        cc2.metric("Frameworks", len(cs["frameworks_found"]))
        cc3.metric("Languages", len(cs["language_breakdown"]))
        cc4.metric("Zombies", cs.get("zombie_count", 0))

    st.markdown('<div class="section-card"><h3>Classification</h3></div>', unsafe_allow_html=True)
    if code_mode:
        zc = data.get("code_scan", {}).get("zombie_count", 0)
        st.bar_chart({"Active": total - zc, "Zombie": zc})
    else:
        st.bar_chart({"Active": s["active"], "Deprecated": s["deprecated"], "Orphaned": s["orphaned"]})

    finding_counts = data.get("finding_counts", {})
    if finding_counts:
        st.markdown('<div class="section-card"><h3>Security Findings</h3></div>', unsafe_allow_html=True)
        sorted_f = sorted(finding_counts.items(), key=lambda x: -x[1])
        for fname, count in sorted_f[:10]:
            if "ZOMBIE" in fname:
                sev = '<span class="zombie-badge">ZOMBIE</span>'
            elif any(w in fname.lower() for w in ["injection", "credential"]):
                sev = '<span class="risk-badge risk-critical">CRITICAL</span>'
            elif any(w in fname.lower() for w in ["debug", "disabled"]):
                sev = '<span class="risk-badge risk-high">HIGH</span>'
            else:
                sev = '<span class="risk-badge risk-medium">INFO</span>'
            st.markdown(f'{sev} {fname} -- **{count}**', unsafe_allow_html=True)

    st.markdown('<div class="section-card"><h3>Endpoint Details</h3></div>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 2, 3])
    with fc1:
        cls_opts = ["active", "zombie"] if code_mode else ["active", "deprecated", "orphaned"]
        cls_def = ["zombie"] if code_mode else ["deprecated", "orphaned"]
        cls_filter = st.multiselect("Classification", cls_opts, default=cls_def, key="cls_f", label_visibility="collapsed")
    with fc2:
        risk_filter = st.multiselect("Risk Level", ["low", "medium", "high", "critical"], default=["critical", "high"], key="risk_f", label_visibility="collapsed")
    with fc3:
        search = st.text_input("Search", key="search_f", placeholder="Search path or file ...", label_visibility="collapsed")

    endpoints = data.get("endpoints", [])
    filtered = endpoints
    if cls_filter:
        filtered = [ep for ep in filtered if ep["classification"] in cls_filter]
    if risk_filter:
        filtered = [ep for ep in filtered if ep["risk_level"] in risk_filter]
    if search:
        sl = search.lower()
        filtered = [ep for ep in filtered if sl in ep["path"].lower() or sl in ep.get("host", "").lower()]

    if not filtered:
        st.info("No endpoints match filters.")
        return

    st.markdown(f"**{len(filtered)} endpoints**")
    for ep in filtered[:100]:
        is_z = ep.get("is_zombie")
        risk = ep["risk_level"]
        if is_z:
            badge = '<span class="zombie-badge">ZOMBIE</span>'
        else:
            cls = f"risk-{risk}"
            badge = f'<span class="risk-badge {cls}">{risk.upper()}</span>'
        findings_str = " | ".join(ep["findings"][:3]) if ep["findings"] else ""
        st.markdown(
            f'<div class="endpoint-row">'
            f'{badge}'
            f'<span class="ep-method">{ep["method"]}</span>'
            f'<span class="ep-path">{ep["path"]}</span>'
            f'<span class="ep-score" style="color:{"#e94560" if is_z else "#53d769" if risk=="low" else "#ffcc00"}">{ep["security_score"]}</span>'
            f'<div class="ep-findings">{findings_str}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def main():
    st.set_page_config(
        page_title="SecureFlow",
        page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    render_header()
    tab_demo, tab_real = st.tabs(["Demo Mode", "Real Mode"])
    with tab_demo:
        render_demo_mode()
    with tab_real:
        render_real_mode()


if __name__ == "__main__":
    main()
