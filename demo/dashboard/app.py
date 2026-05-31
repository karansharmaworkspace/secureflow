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
import plotly.express as px
import plotly.graph_objects as go

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
LOGO_PATH = PROJECT_ROOT / "logo.jpeg"

if not LOGO_PATH.exists():
    for candidate in [Path.cwd() / "logo.jpeg", Path.cwd().parent / "logo.jpeg", SCRIPT_DIR / "logo.jpeg"]:
        if candidate.exists():
            LOGO_PATH = candidate
            break

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

FRAMEWORK_LANG = {
    "python_flask": "Python", "python_fastapi": "Python", "python_django": "Python",
    "javascript_express": "JavaScript", "javascript_nestjs": "TypeScript",
    "java_spring": "Java", "go_gin": "Go",
}

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


def scan_codebase(upload_bytes: bytes) -> dict:
    endpoints = []
    files_scanned = 0
    frameworks_found = set()

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(upload_bytes)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp)

        for root, _dirs, files in os.walk(tmp):
            for fname in files:
                fpath = os.path.join(root, fname)
                ext = Path(fname).suffix.lower()
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
                            method_map = {"route": "ANY", "add_url_rule": "ANY", "api_view": "ANY", "add_api_route": "ANY"}
                            method = method_map.get(method.lower(), method.upper())
                            frameworks_found.add(framework)
                            good_hits = [label for pat, label in SECURITY_GOOD_PATTERNS if pat.search(content)]
                            bad_hits = [label for pat, label in SECURITY_BAD_PATTERNS if pat.search(content)]
                            parts = rel_path.split(os.sep)
                            project_path = os.sep.join(parts[1:]) if len(parts) > 1 else rel_path
                            endpoints.append({
                                "file": project_path, "framework": framework,
                                "language": FRAMEWORK_LANG.get(framework, "Unknown"),
                                "method": method, "route": route,
                                "line": content[:match.start()].count("\n") + 1,
                                "security_good": good_hits, "security_bad": bad_hits,
                            })

    seen = set()
    unique = []
    for ep in endpoints:
        key = (ep["route"], ep["method"], ep["framework"])
        if key not in seen:
            seen.add(key)
            unique.append(ep)
    return {"files_scanned": files_scanned, "frameworks_found": sorted(frameworks_found), "total_routes": len(unique), "endpoints": unique}


def score_code_endpoint(ep: dict) -> dict:
    good = len(set(ep.get("security_good", [])))
    bad = len(set(ep.get("security_bad", [])))
    total_patterns = good + bad
    base = (good / total_patterns) * 70 + 30 if total_patterns > 0 else 50
    score = max(0, min(100, base - bad * 12))

    findings = []
    zombie_score = 0
    route = ep.get("route", "")
    file_path = ep.get("file", "")
    full_context = f"{route} {file_path}"

    for pat, label in ZOMBIE_INDICATORS:
        if pat.search(full_context):
            zombie_score += 1
            findings.append(f"[ZOMBIE] {label}")
    if route in ("/health", "/ping", "/alive", "/status", "/version", "/"):
        zombie_score += 1
        findings.append("[ZOMBIE] Generic health/status endpoint")
    if ep.get("method") == "ANY" and not any(m in route.lower() for m in ["get", "post", "put", "delete"]):
        zombie_score += 0.5

    for label in ep.get("security_bad", []):
        findings.append(f"[RISK] {label}")
    for label in ep.get("security_good", []):
        findings.append(f"[OK] {label}")
    if not ep.get("security_good"):
        findings.append("[WARN] No security patterns detected in file")

    is_zombie = zombie_score >= 2
    risk = "low" if score >= 80 else "medium" if score >= 60 else "high" if score >= 40 else "critical"
    return {
        "security_score": round(score, 1), "risk_level": risk,
        "classification": "zombie" if is_zombie else "active",
        "is_zombie": is_zombie, "findings": findings,
        "security_good_count": good, "security_bad_count": bad,
    }


CUSTOM_CSS = """
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; }
    .stTabs [data-baseweb="tab"] { padding: 12px 32px; font-size: 15px; font-weight: 600; border-bottom: 3px solid transparent; }
    .stTabs [aria-selected="true"] { border-bottom-color: #e94560; color: #fff; }
    div[data-testid="stMetric"] { background: #16213e; border: 1px solid #0f3460; border-radius: 12px; padding: 20px 24px; min-height: 100px; }
    div[data-testid="stMetric"] label { color: #8899aa; font-size: 13px; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff; font-size: 28px; font-weight: 700; }
    .hero-box { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 12px; padding: 40px; margin-bottom: 24px; text-align: center; }
    .hero-box h1 { color: #fff; font-size: 42px; margin: 0; font-weight: 800; letter-spacing: -1px; }
    .hero-box p { color: #8899aa; font-size: 16px; margin-top: 8px; }
    .section-card { background: #16213e; border: 1px solid #0f3460; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
    .section-card h3 { color: #fff; font-size: 16px; margin: 0 0 16px 0; font-weight: 600; }
    .zombie-badge { display: inline-block; background: #e94560; color: #fff; padding: 2px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; margin-right: 8px; }
    .risk-low { background: #53d769; } .risk-medium { background: #ffcc00; color: #1a1a2e; }
    .risk-high { background: #ff8c00; } .risk-critical { background: #e94560; }
    .risk-badge { display: inline-block; padding: 2px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .endpoint-row { background: #0f1a30; border: 1px solid #1a2a4a; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; font-size: 13px; }
    .endpoint-row:hover { border-color: #0f3460; }
    .ep-method { font-weight: 700; margin-right: 8px; }
    .ep-path { font-family: 'Cascadia Code', monospace; color: #ccc; }
    .ep-score { float: right; font-weight: 700; }
    .ep-findings { color: #8899aa; font-size: 12px; margin-top: 6px; }
    .upload-zone { border: 2px dashed #0f3460; border-radius: 16px; padding: 60px 40px; text-align: center; background: #0f1a30; }
    .upload-zone h3 { color: #fff; margin: 0 0 8px 0; } .upload-zone p { color: #8899aa; margin: 0; }
</style>
"""

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#16213e",
    plot_bgcolor="#16213e",
    font=dict(color="#e0e0e0"),
    margin=dict(l=20, r=20, t=40, b=20),
    height=350,
)


def get_logo():
    return str(LOGO_PATH) if LOGO_PATH.exists() else None


def render_header():
    logo = get_logo()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    import base64
    if logo:
        with open(logo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        img_html = f"<img src='data:image/jpeg;base64,{b64}' width='120' style='border-radius:16px;'>"
    else:
        img_html = "<div style='font-size:80px;line-height:120px;'>&#9760;</div>"
    st.markdown(
        f"""<div class="hero-box"><div style="display:flex;align-items:center;justify-content:center;gap:24px;">
        {img_html}<div style="text-align:left;"><h1>SecureFlow</h1><p>API Security Posture Scanner</p></div></div></div>""",
        unsafe_allow_html=True,
    )


def render_demo_mode():
    st.markdown('<div class="section-card"><h3>Demo Mode</h3>Run the synthetic pipeline on 1,13,836 simulated banking API endpoints.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        run_btn = st.button("Run Pipeline", type="primary", key="run_demo", use_container_width=True)
    with col2:
        cached_btn = st.button("Load Cached", key="load_cached", use_container_width=True)

    if run_btn:
        tmp_dir = tempfile.mkdtemp()
        parquet_path = os.path.join(tmp_dir, "endpoint_features.parquet")
        scan_path = os.path.join(tmp_dir, "registry_scan.json")
        with st.spinner("Generating synthetic data ..."):
            import subprocess
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "demo" / "traffic-generator" / "simulate.py"), "--generate-features", parquet_path],
                cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                st.error(f"Data generation failed:\n{result.stderr[:500]}")
                return
        with st.spinner("Scanning registry ..."):
            sys.path.insert(0, str(SCRIPT_DIR))
            from registry_scanner import scan
            st.session_state["scan_data"] = scan(parquet_path, scan_path)

    if cached_btn:
        scan_json = PROJECT_ROOT / "demo" / "test-data" / "registry_scan.json"
        if scan_json.exists():
            with open(scan_json, "r", encoding="utf-8") as f:
                st.session_state["scan_data"] = json.load(f)
        else:
            st.warning("No cached results found. Run the pipeline first.")

    if "scan_data" in st.session_state:
        render_results(st.session_state["scan_data"])


def render_real_mode():
    st.markdown('<div class="section-card"><h3>Real Mode</h3>Upload your codebase zip. SecureFlow scans for API routes, identifies zombie APIs, and scores security posture.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload codebase zip", type=["zip"], label_visibility="collapsed", max_upload_size=4096)

    if uploaded is None:
        st.markdown('<div class="upload-zone"><h3>Drop your codebase here</h3><p>Flask, FastAPI, Express, NestJS, Spring Boot, Gin and more</p></div>', unsafe_allow_html=True)
        if "real_data" in st.session_state:
            render_results(st.session_state["real_data"], code_mode=True)
        return

    if "real_data" not in st.session_state or st.session_state.get("real_file_name") != uploaded.name:
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
        risk_counts, lang_counts, fw_counts = defaultdict(int), defaultdict(int), defaultdict(int)
        for ep in scored:
            risk_counts[ep["risk_level"]] += 1
            lang_counts[ep["language"]] += 1
            fw_counts[ep["framework"]] += 1
        finding_counts = defaultdict(int)
        for ep in scored:
            for f in ep["findings"]:
                finding_counts[f] += 1

        st.session_state["real_data"] = {
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_endpoints": total,
            "summary": {"active": total - zombie_count, "deprecated": 0, "orphaned": zombie_count, "avg_security_score": avg_score, "total_annual_cost_inr": 0, "zombie_annual_cost_inr": 0},
            "finding_counts": dict(finding_counts),
            "endpoints": [
                {"endpoint_key": f"{ep['framework']}|{ep['method']}|{ep['route']}", "host": ep["file"], "domain": ep["language"], "api_version": 0,
                 "method": ep["method"], "path": ep["route"], "traffic_level": "unknown",
                 "classification": "zombie" if ep["is_zombie"] else "active", "security_score": ep["security_score"],
                 "is_zombie": 1 if ep["is_zombie"] else 0, "annual_cost_inr": 0, "risk_level": ep["risk_level"], "findings": ep["findings"]}
                for ep in scored
            ],
            "code_scan": {"files_scanned": result["files_scanned"], "frameworks_found": result["frameworks_found"],
                          "language_breakdown": dict(lang_counts), "framework_breakdown": dict(fw_counts),
                          "risk_breakdown": dict(risk_counts), "zombie_count": zombie_count},
        }
        st.session_state["real_file_name"] = uploaded.name

    render_results(st.session_state["real_data"], code_mode=True)


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
        co1, co2, co3 = st.columns(3)
        co1.metric("Total Annual", f"INR {s['total_annual_cost_inr']:,.0f}")
        co2.metric("Zombie Cost", f"INR {s['zombie_annual_cost_inr']:,.0f}")
        co3.metric("Savings", f"INR {s['zombie_annual_cost_inr']:,.0f}/yr")

    if code_mode and "code_scan" in data:
        cs = data["code_scan"]
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("Files Scanned", cs["files_scanned"])
        cc2.metric("Frameworks", len(cs["frameworks_found"]))
        cc3.metric("Languages", len(cs["language_breakdown"]))
        cc4.metric("Zombies", cs.get("zombie_count", 0))

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="section-card"><h3>Classification Distribution</h3></div>', unsafe_allow_html=True)
        if code_mode:
            zc = data.get("code_scan", {}).get("zombie_count", 0)
            fig_pie = px.pie(values=[total - zc, zc], names=["Active", "Zombie"],
                             color_discrete_sequence=["#53d769", "#e94560"], hole=0.4)
        else:
            fig_pie = px.pie(values=[s["active"], s["deprecated"], s["orphaned"]],
                             names=["Active", "Deprecated", "Orphaned"],
                             color_discrete_sequence=["#53d769", "#ffcc00", "#e94560"], hole=0.4)
        fig_pie.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.markdown('<div class="section-card"><h3>Risk Distribution</h3></div>', unsafe_allow_html=True)
        endpoints = data.get("endpoints", [])
        risk_data = defaultdict(int)
        for ep in endpoints:
            risk_data[ep["risk_level"]] += 1
        risk_order = ["critical", "high", "medium", "low"]
        risk_colors = {"critical": "#e94560", "high": "#ff8c00", "medium": "#ffcc00", "low": "#53d769"}
        fig_risk = go.Figure(go.Bar(
            x=[risk_data.get(r, 0) for r in risk_order],
            y=risk_order,
            orientation="h",
            marker_color=[risk_colors[r] for r in risk_order],
            text=[risk_data.get(r, 0) for r in risk_order],
            textposition="auto",
        ))
        fig_risk.update_layout(**PLOTLY_LAYOUT, xaxis_title="Count", yaxis_title="")
        st.plotly_chart(fig_risk, use_container_width=True)

    finding_counts = data.get("finding_counts", {})
    if finding_counts:
        st.markdown('<div class="section-card"><h3>Security Findings</h3></div>', unsafe_allow_html=True)
        sorted_f = sorted(finding_counts.items(), key=lambda x: -x[1])[:15]
        labels = [f[0] for f in sorted_f]
        values = [f[1] for f in sorted_f]
        colors = ["#e94560" if "ZOMBIE" in l else "#ff8c00" if any(w in l.lower() for w in ["injection", "credential", "debug"]) else "#0f3460" for l in labels]
        fig_find = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors, text=values, textposition="auto"))
        fig_find.update_layout(**PLOTLY_LAYOUT, height=max(300, len(labels) * 32), xaxis_title="Occurrences", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_find, use_container_width=True)

    if code_mode and "code_scan" in data:
        cs = data["code_scan"]
        chart_col3, chart_col4 = st.columns(2)
        with chart_col3:
            st.markdown('<div class="section-card"><h3>Framework Breakdown</h3></div>', unsafe_allow_html=True)
            fw = cs.get("framework_breakdown", {})
            if fw:
                fig_fw = px.bar(x=list(fw.keys()), y=list(fw.values()), color=list(fw.keys()),
                                color_discrete_sequence=px.colors.qualitative.Set2)
                fig_fw.update_layout(**PLOTLY_LAYOUT, xaxis_title="", yaxis_title="Routes", showlegend=False)
                st.plotly_chart(fig_fw, use_container_width=True)
        with chart_col4:
            st.markdown('<div class="section-card"><h3>Language Breakdown</h3></div>', unsafe_allow_html=True)
            lang = cs.get("language_breakdown", {})
            if lang:
                fig_lang = px.pie(values=list(lang.values()), names=list(lang.keys()), hole=0.5,
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_lang.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig_lang, use_container_width=True)

    if endpoints:
        st.markdown('<div class="section-card"><h3>Score Distribution</h3></div>', unsafe_allow_html=True)
        scores = [ep["security_score"] for ep in endpoints]
        fig_hist = px.histogram(x=scores, nbins=20, color_discrete_sequence=["#0f3460"])
        fig_hist.update_layout(**PLOTLY_LAYOUT, xaxis_title="Security Score", yaxis_title="Count")
        st.plotly_chart(fig_hist, use_container_width=True)

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
        badge = '<span class="zombie-badge">ZOMBIE</span>' if is_z else f'<span class="risk-badge risk-{risk}">{risk.upper()}</span>'
        findings_str = " | ".join(ep["findings"][:3]) if ep["findings"] else ""
        color = "#e94560" if is_z else "#53d769" if risk == "low" else "#ffcc00"
        st.markdown(
            f'<div class="endpoint-row">{badge}<span class="ep-method">{ep["method"]}</span>'
            f'<span class="ep-path">{ep["path"]}</span>'
            f'<span class="ep-score" style="color:{color}">{ep["security_score"]}</span>'
            f'<div class="ep-findings">{findings_str}</div></div>',
            unsafe_allow_html=True,
        )


def main():
    st.set_page_config(page_title="SecureFlow", page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None, layout="wide", initial_sidebar_state="collapsed")
    render_header()
    tab_demo, tab_real = st.tabs(["Demo Mode", "Real Mode"])
    with tab_demo:
        render_demo_mode()
    with tab_real:
        render_real_mode()


if __name__ == "__main__":
    main()
