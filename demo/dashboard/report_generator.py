#!/usr/bin/env python3
"""
SecureFlow Everywhere - HTML Report Generator

Reads registry_scan.json and produces a self-contained HTML dashboard with:
  - Summary cards (active/deprecated/orphaned counts, avg score)
  - Cost analysis
  - CSS-only pie chart for classification distribution
  - Domain breakdown table
  - Sortable endpoint table with color-coded risk levels
  - Security findings frequency chart
"""

import argparse
import json
import os
import sys
from html import escape


def bar_chart_html(label, value, max_val, color):
    pct = (value / max_val * 100) if max_val > 0 else 0
    return (
        f'<div class="bar-row">'
        f'<span class="bar-label">{escape(str(label))}</span>'
        f'<div class="bar-track">'
        f'<div class="bar-fill" style="width:{pct:.1f}%;background:{color}"></div>'
        f'</div>'
        f'<span class="bar-value">{value}</span>'
        f'</div>'
    )


def generate_html(scan_data):
    s = scan_data["summary"]
    endpoints = scan_data["endpoints"]
    finding_counts = scan_data.get("finding_counts", {})

    active = s["active"]
    deprecated = s["deprecated"]
    orphaned = s["orphaned"]
    total = scan_data["total_endpoints"]
    avg_score = s["avg_security_score"]
    total_cost = s["total_annual_cost_inr"]
    zombie_cost = s["zombie_annual_cost_inr"]
    savings = zombie_cost

    # Pie chart percentages
    a_pct = (active / total * 100) if total else 0
    d_pct = (deprecated / total * 100) if total else 0
    o_pct = (orphaned / total * 100) if total else 0

    # Domain breakdown
    domains = {}
    for ep in endpoints:
        d = ep["domain"]
        if d not in domains:
            domains[d] = {"active": 0, "deprecated": 0, "orphaned": 0, "scores": []}
        domains[d][ep["classification"]] += 1
        domains[d]["scores"].append(ep["security_score"])

    domain_rows = ""
    for dname in sorted(domains.keys()):
        dc = domains[dname]
        davg = round(sum(dc["scores"]) / len(dc["scores"]), 1) if dc["scores"] else 0
        domain_rows += (
            f'<tr>'
            f'<td>{escape(dname)}</td>'
            f'<td class="num">{dc["active"]}</td>'
            f'<td class="num">{dc["deprecated"]}</td>'
            f'<td class="num">{dc["orphaned"]}</td>'
            f'<td class="num">{davg}</td>'
            f'</tr>\n'
        )

    # Endpoint rows
    ep_rows = ""
    risk_colors = {"critical": "#e94560", "high": "#ff8c00", "medium": "#ffcc00", "low": "#53d769"}
    for ep in endpoints:
        rc = risk_colors.get(ep["risk_level"], "#888")
        findings_str = escape(" | ".join(ep["findings"])) if ep["findings"] else "None"
        ep_rows += (
            f'<tr class="risk-{ep["risk_level"]}" title="{findings_str}">'
            f'<td class="mono">{escape(ep["host"])}</td>'
            f'<td class="mono">{escape(ep["method"])}</td>'
            f'<td class="mono path-cell">{escape(ep["path"][:60])}</td>'
            f'<td>{escape(ep["domain"])}</td>'
            f'<td class="num">v{ep["api_version"]}</td>'
            f'<td class="cls-{ep["classification"]}">{ep["classification"]}</td>'
            f'<td class="num">{ep["security_score"]}</td>'
            f'<td class="risk-badge" style="background:{rc}">{ep["risk_level"]}</td>'
            f'<td class="num">INR {ep["annual_cost_inr"]:,.0f}</td>'
            f'</tr>\n'
        )

    # Finding bars
    max_find = max(finding_counts.values()) if finding_counts else 1
    finding_colors = {
        "Low authentication coverage": "#e94560",
        "100% synthetic traffic": "#ff8c00",
        "No recent real traffic (>60 days)": "#ffcc00",
        "High error rate (4xx+5xx > 10%)": "#ffcc00",
        "Minimal user-agent diversity": "#0f3460",
        "Minimal source IP diversity": "#0f3460",
        "Classified as zombie endpoint": "#e94560",
    }
    finding_bars = ""
    for fname in sorted(finding_counts.keys(), key=lambda x: finding_counts[x], reverse=True):
        fc = finding_counts[fname]
        color = finding_colors.get(fname, "#0f3460")
        finding_bars += bar_chart_html(fname, fc, max_find, color)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SecureFlow Everywhere - API Registry Report</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#1a1a2e; color:#e0e0e0; font-family:'Segoe UI',system-ui,sans-serif; padding:24px; }}
h1 {{ color:#fff; font-size:28px; margin-bottom:4px; }}
.subtitle {{ color:#888; font-size:14px; margin-bottom:24px; }}
.cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }}
.card {{ background:#16213e; border-radius:12px; padding:20px; text-align:center; }}
.card .num {{ font-size:36px; font-weight:700; }}
.card .label {{ font-size:13px; color:#aaa; margin-top:4px; }}
.card.active-card .num {{ color:#53d769; }}
.card.deprecated-card .num {{ color:#ffcc00; }}
.card.orphaned-card .num {{ color:#e94560; }}
.card.score-card .num {{ color:#0f3460; background:#0f3460; color:#fff; display:inline-block; padding:4px 16px; border-radius:8px; }}
.section {{ background:#16213e; border-radius:12px; padding:20px; margin-bottom:24px; }}
.section h2 {{ font-size:18px; margin-bottom:16px; color:#fff; }}
.pie-wrap {{ display:flex; align-items:center; gap:32px; }}
.pie {{ width:180px; height:180px; border-radius:50%; background:conic-gradient(#53d769 0% {a_pct:.1f}%, #ffcc00 {a_pct:.1f}% {a_pct+d_pct:.1f}%, #e94560 {a_pct+d_pct:.1f}% 100%); }}
.pie-legend {{ font-size:14px; line-height:2; }}
.pie-legend span {{ display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:8px; vertical-align:middle; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ text-align:left; padding:8px 10px; border-bottom:2px solid #0f3460; color:#aaa; font-weight:600; }}
td {{ padding:7px 10px; border-bottom:1px solid #1a1a2e; }}
.num {{ text-align:right; }}
.mono {{ font-family:'Cascadia Code','Fira Code',monospace; font-size:12px; }}
.path-cell {{ max-width:260px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.risk-badge {{ color:#fff; text-align:center; border-radius:4px; font-size:11px; font-weight:600; text-transform:uppercase; }}
.risk-critical td {{ background:rgba(233,69,96,0.1); }}
.risk-high td {{ background:rgba(255,140,0,0.08); }}
.risk-medium td {{ background:rgba(255,204,0,0.05); }}
.risk-low td {{ background:rgba(83,215,105,0.05); }}
.cls-active {{ color:#53d769; font-weight:600; }}
.cls-deprecated {{ color:#ffcc00; font-weight:600; }}
.cls-orphaned {{ color:#e94560; font-weight:600; }}
.cost-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
.cost-item {{ text-align:center; }}
.cost-item .val {{ font-size:24px; font-weight:700; color:#fff; }}
.cost-item .lbl {{ font-size:12px; color:#aaa; margin-top:4px; }}
.bar-row {{ display:flex; align-items:center; gap:10px; margin-bottom:6px; }}
.bar-label {{ width:280px; font-size:12px; text-align:right; color:#ccc; }}
.bar-track {{ flex:1; height:18px; background:#1a1a2e; border-radius:4px; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:4px; transition:width 0.3s; }}
.bar-value {{ width:60px; font-size:12px; color:#aaa; text-align:right; }}
.filters {{ display:flex; gap:12px; margin-bottom:16px; flex-wrap:wrap; }}
.filters label {{ font-size:13px; cursor:pointer; padding:4px 12px; border-radius:6px; background:#0f3460; color:#fff; }}
.filters input[type=checkbox] {{ display:none; }}
.filters input[type=checkbox]:not(:checked) + span {{ opacity:0.4; }}
.ep-table-wrap {{ max-height:600px; overflow-y:auto; }}
</style>
</head>
<body>
<h1>SecureFlow Everywhere</h1>
<p class="subtitle">API Registry Security Posture Report | Scanned: {escape(scan_data["scan_timestamp"][:19])} | {total} endpoints</p>

<div class="cards">
  <div class="card active-card"><div class="num">{active}</div><div class="label">Active</div></div>
  <div class="card deprecated-card"><div class="num">{deprecated}</div><div class="label">Deprecated</div></div>
  <div class="card orphaned-card"><div class="num">{orphaned}</div><div class="label">Orphaned</div></div>
  <div class="card score-card"><div class="num">{avg_score}</div><div class="label">Avg Security Score</div></div>
</div>

<div class="section">
  <h2>Cost Analysis</h2>
  <div class="cost-grid">
    <div class="cost-item"><div class="val">INR {total_cost:,.0f}</div><div class="lbl">Total Annual API Cost</div></div>
    <div class="cost-item"><div class="val" style="color:#e94560">INR {zombie_cost:,.0f}</div><div class="lbl">Zombie Endpoint Cost</div></div>
    <div class="cost-item"><div class="val" style="color:#53d769">INR {savings:,.0f}</div><div class="lbl">Potential Savings / Year</div></div>
  </div>
</div>

<div class="section">
  <h2>Classification Distribution</h2>
  <div class="pie-wrap">
    <div class="pie"></div>
    <div class="pie-legend">
      <div><span style="background:#53d769"></span>Active: {active} ({a_pct:.1f}%)</div>
      <div><span style="background:#ffcc00"></span>Deprecated: {deprecated} ({d_pct:.1f}%)</div>
      <div><span style="background:#e94560"></span>Orphaned: {orphaned} ({o_pct:.1f}%)</div>
    </div>
  </div>
</div>

<div class="section">
  <h2>Domain Breakdown</h2>
  <table>
    <thead><tr><th>Domain</th><th>Active</th><th>Deprecated</th><th>Orphaned</th><th>Avg Score</th></tr></thead>
    <tbody>{domain_rows}</tbody>
  </table>
</div>

<div class="section">
  <h2>Security Findings</h2>
  {finding_bars}
</div>

<div class="section">
  <h2>Endpoint Inventory ({total})</h2>
  <div class="ep-table-wrap">
  <table>
    <thead><tr><th>Host</th><th>Method</th><th>Path</th><th>Domain</th><th>Ver</th><th>Classification</th><th>Score</th><th>Risk</th><th>Cost (INR)</th></tr></thead>
    <tbody>{ep_rows}</tbody>
  </table>
  </div>
</div>

</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="SecureFlow Everywhere - Report Generator")
    parser.add_argument("--input", default="demo/test-data/registry_scan.json",
                        help="Path to registry scan JSON")
    parser.add_argument("--output", default="demo/test-data/registry_report.html",
                        help="Path to output HTML")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERR] Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = generate_html(data)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Report generated: {args.output}")


if __name__ == "__main__":
    main()
