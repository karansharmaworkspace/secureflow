#!/usr/bin/env python3
"""
Union Bank-scale API Traffic Simulator
Generates 10,000+ endpoints across 15+ Indian banking domains with
realistic traffic patterns that make zombie detection genuinely challenging.
"""

import json
import logging
import math
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s", stream=sys.stdout)
logger = logging.getLogger("simulate")

# ──────────────────────────────────────────────
# DOMAIN CONFIG
# ──────────────────────────────────────────────

@dataclass
class DomainConfig:
    name: str
    host: str
    base_path: str
    versions: List[int]
    traffic_level: str
    endpoint_templates: List[Dict[str, Any]]
    zombie_rate_by_version: Dict[int, float]
    zombie_rate_multiplier: float


DOMAINS: List[DomainConfig] = [
    DomainConfig(
        name="Accounts", host="api.bank.example.com", base_path="/api",
        versions=[1, 2, 3], traffic_level="critical",
        endpoint_templates=[
            {"path": "/accounts/{id}/balance", "methods": ["GET"], "param_count": 1},
            {"path": "/accounts/{id}/statement", "methods": ["GET"], "param_count": 1},
            {"path": "/accounts/{id}/details", "methods": ["GET"], "param_count": 1},
        ],
        zombie_rate_by_version={1: 0.40, 2: 0.20, 3: 0.08}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="UPI", host="upi.bank.example.com", base_path="/upi",
        versions=[1, 2, 3], traffic_level="critical",
        endpoint_templates=[
            {"path": "/pay", "methods": ["POST"], "param_count": 0},
            {"path": "/collect", "methods": ["POST"], "param_count": 0},
            {"path": "/validate-vpa", "methods": ["POST"], "param_count": 0},
            {"path": "/transaction-history", "methods": ["GET"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.35, 2: 0.18, 3: 0.06}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="NEFT", host="neft.bank.example.com", base_path="/neft",
        versions=[1, 2, 3], traffic_level="high",
        endpoint_templates=[
            {"path": "/transfer", "methods": ["POST"], "param_count": 0},
            {"path": "/status/{txn_id}", "methods": ["GET"], "param_count": 1},
            {"path": "/beneficiary", "methods": ["GET", "POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.40, 2: 0.22, 3: 0.10}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="IMPS", host="imps.bank.example.com", base_path="/imps",
        versions=[1, 2, 3], traffic_level="high",
        endpoint_templates=[
            {"path": "/payment", "methods": ["POST"], "param_count": 0},
            {"path": "/status/{txn_id}", "methods": ["GET"], "param_count": 1},
            {"path": "/validate-mobile", "methods": ["POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.38, 2: 0.20, 3: 0.09}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="RTGS", host="rtgs.bank.example.com", base_path="/rtgs",
        versions=[1, 2, 3], traffic_level="high",
        endpoint_templates=[
            {"path": "/transfer", "methods": ["POST"], "param_count": 0},
            {"path": "/status/{txn_id}", "methods": ["GET"], "param_count": 1},
            {"path": "/beneficiary", "methods": ["GET", "POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.40, 2: 0.22, 3: 0.10}, zombie_rate_multiplier=0.9,
    ),
    DomainConfig(
        name="Cards", host="cards.bank.example.com", base_path="/cards",
        versions=[1, 2, 3], traffic_level="high",
        endpoint_templates=[
            {"path": "/transactions", "methods": ["GET"], "param_count": 0},
            {"path": "/statement", "methods": ["GET"], "param_count": 1},
            {"path": "/block", "methods": ["POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.45, 2: 0.25, 3: 0.12}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="Loans", host="loans.bank.example.com", base_path="/loans",
        versions=[1, 2, 3], traffic_level="moderate",
        endpoint_templates=[
            {"path": "/statement/{id}", "methods": ["GET"], "param_count": 1},
            {"path": "/details/{id}", "methods": ["GET"], "param_count": 1},
            {"path": "/eligibility", "methods": ["POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.45, 2: 0.28, 3: 0.15}, zombie_rate_multiplier=1.1,
    ),
    DomainConfig(
        name="KYC", host="kyc.bank.example.com", base_path="/kyc",
        versions=[1, 2, 3], traffic_level="moderate",
        endpoint_templates=[
            {"path": "/verify", "methods": ["POST"], "param_count": 0},
            {"path": "/status/{ref_id}", "methods": ["GET"], "param_count": 1},
            {"path": "/document-upload", "methods": ["POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.35, 2: 0.20, 3: 0.08}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="Forex", host="forex.bank.example.com", base_path="/forex",
        versions=[1, 2, 3], traffic_level="moderate",
        endpoint_templates=[
            {"path": "/rates/{pair}", "methods": ["GET"], "param_count": 1},
            {"path": "/convert", "methods": ["POST"], "param_count": 0},
            {"path": "/remittance", "methods": ["POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.42, 2: 0.25, 3: 0.12}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="FixedDeposits", host="fd.bank.example.com", base_path="/fd",
        versions=[1, 2, 3], traffic_level="moderate",
        endpoint_templates=[
            {"path": "/create", "methods": ["POST"], "param_count": 0},
            {"path": "/details/{id}", "methods": ["GET"], "param_count": 1},
            {"path": "/rates", "methods": ["GET"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.40, 2: 0.24, 3: 0.10}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="RecurringDeposits", host="rd.bank.example.com", base_path="/rd",
        versions=[1, 2, 3], traffic_level="moderate",
        endpoint_templates=[
            {"path": "/create", "methods": ["POST"], "param_count": 0},
            {"path": "/details/{id}", "methods": ["GET"], "param_count": 1},
            {"path": "/missed-installment", "methods": ["GET"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.42, 2: 0.26, 3: 0.12}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="Cheque", host="cheque.bank.example.com", base_path="/cheque",
        versions=[1, 2], traffic_level="low",
        endpoint_templates=[
            {"path": "/status/{id}", "methods": ["GET"], "param_count": 1},
            {"path": "/stop-payment", "methods": ["POST"], "param_count": 0},
            {"path": "/book-request", "methods": ["POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.50, 2: 0.30}, zombie_rate_multiplier=1.1,
    ),
    DomainConfig(
        name="Notifications", host="notify.bank.example.com", base_path="/notifications",
        versions=[1, 2, 3], traffic_level="low",
        endpoint_templates=[
            {"path": "/email-send", "methods": ["POST"], "param_count": 0},
            {"path": "/sms-send", "methods": ["POST"], "param_count": 0},
            {"path": "/history", "methods": ["GET"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.45, 2: 0.28, 3: 0.15}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="Admin", host="admin.bank.example.com", base_path="/admin",
        versions=[1, 2], traffic_level="batch",
        endpoint_templates=[
            {"path": "/users", "methods": ["GET", "POST"], "param_count": 0},
            {"path": "/audit-log", "methods": ["GET"], "param_count": 0},
            {"path": "/config", "methods": ["GET", "PUT"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.55, 2: 0.35}, zombie_rate_multiplier=1.2,
    ),
    DomainConfig(
        name="Reporting", host="reporting.bank.example.com", base_path="/reports",
        versions=[1, 2, 3], traffic_level="low",
        endpoint_templates=[
            {"path": "/transactions", "methods": ["GET"], "param_count": 0},
            {"path": "/summary", "methods": ["GET"], "param_count": 0},
            {"path": "/export", "methods": ["GET", "POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.50, 2: 0.32, 3: 0.18}, zombie_rate_multiplier=1.1,
    ),
    DomainConfig(
        name="AuthGateway", host="auth.bank.example.com", base_path="/auth",
        versions=[1, 2, 3], traffic_level="critical",
        endpoint_templates=[
            {"path": "/login", "methods": ["POST"], "param_count": 0},
            {"path": "/refresh", "methods": ["POST"], "param_count": 0},
            {"path": "/otp-generate", "methods": ["POST"], "param_count": 0},
            {"path": "/otp-validate", "methods": ["POST"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.30, 2: 0.15, 3: 0.05}, zombie_rate_multiplier=0.8,
    ),
    DomainConfig(
        name="DigitalWallet", host="wallet.bank.example.com", base_path="/wallet",
        versions=[1, 2, 3], traffic_level="moderate",
        endpoint_templates=[
            {"path": "/balance", "methods": ["GET"], "param_count": 0},
            {"path": "/add-money", "methods": ["POST"], "param_count": 0},
            {"path": "/transactions", "methods": ["GET"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.40, 2: 0.22, 3: 0.10}, zombie_rate_multiplier=1.0,
    ),
    DomainConfig(
        name="ServiceRegistry", host="registry.bank.example.com", base_path="/registry",
        versions=[1, 2], traffic_level="batch",
        endpoint_templates=[
            {"path": "/services", "methods": ["GET"], "param_count": 0},
            {"path": "/register", "methods": ["POST"], "param_count": 0},
            {"path": "/health", "methods": ["GET"], "param_count": 0},
        ],
        zombie_rate_by_version={1: 0.50, 2: 0.35}, zombie_rate_multiplier=1.2,
    ),
]


# ──────────────────────────────────────────────
# REALISTIC UA, IP, STATUS DISTRIBUTIONS
# ──────────────────────────────────────────────

REAL_USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Android 14; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/17.4",
    "Mozilla/5.0 (Linux; Android 14; SAMSUNG SM-S928B) AppleWebKit/537.36 Chrome/122.0.0.0",
    "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Dalvik/2.1.0 (Linux; U; Android 14; Pixel 8 Pro Build/AP1A.240505.002)",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 Chrome/120.0.6099.230",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/124.0.2478.80",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0.6312.105",
    "Mozilla/5.0 (iPod touch; CPU iPhone OS 17_3 like Mac OS X) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 13; MI 11 Lite) AppleWebKit/537.36 Chrome/120.0.6099.230",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/124.0.0.0 Safari/537.36",
    "UnionBankApp/3.4.1 (Android 14; SM-S928B)",
    "UnionBankApp/3.4.1 (iOS 17.4; iPhone15,3)",
    "UnionBankApp/3.3.0 (Android 13; Pixel 7)",
    "UnionBankNetBanking/2.1.0 CFNetwork/1410.0.3 Darwin/22.6.0",
    "axios/1.6.7 (Node.js/20.11.0)",
    "python-requests/2.31.0 (partner-integration)",
]

SYNTHETIC_USER_AGENTS = [
    "Prometheus/1.8.0",
    "Prometheus/2.52.0",
    "kube-probe/1.27",
    "kube-probe/1.28",
    "kube-probe/1.29",
    "Datadog Agent/7.52.0",
    "Datadog Agent/7.48.0",
    "Datadog Agent/7.55.0",
    "healthcheck/1.0",
    "UptimeRobot/1.0",
    "Amazon-Route53-Health-Check/1.0",
    "NewRelic-Synthetics/1.0",
    "GCP-HealthCheck/1.0",
    "Azure-LoadBalancer/1.0",
    "Dynatrace-Synthetic/1.0",
    "F5-HealthChecker/1.0",
    "Consul-Agent/1.18.0",
    "Telegraf/1.30.0",
    "Zabbix/6.4.0",
    "Nagios/4.4.6",
    "Selenium/4.18.1 (monitoring-script)",
    "Playwright/1.42.0 (e2e-test)",
    "curl/8.4.0 (cron-job)",
    "Wget/1.21.4 (cron-job)",
    "Apache-HttpClient/4.5.14 (internal-batch)",
]

REAL_SOURCE_IPS = [
    f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(2,254)}"
    for _ in range(100)
]

SYNTHETIC_SOURCE_IPS = [
    f"10.0.0.{i}" for i in range(1, 11)
]


def traffic_level_to_base_calls(level: str) -> Tuple[int, int]:
    """Return (daily_call_mean, daily_call_stddev) for a traffic level."""
    mapping = {
        "critical":  (500_000, 100_000),
        "high":      (100_000, 40_000),
        "moderate":  (20_000,  10_000),
        "low":       (2_000,    1_500),
        "batch":     (500,       200),
    }
    return mapping.get(level, (10_000, 5_000))


def version_traffic_multiplier(version: int) -> float:
    """Higher versions get more traffic (clients migrate forward)."""
    return {1: 0.3, 2: 0.8, 3: 1.0}.get(version, 0.5)


# ──────────────────────────────────────────────
# SCALE EXPANSION — Union Bank: 10,000+ endpoints
# ──────────────────────────────────────────────

SCALE_RESOURCES: Dict[str, List[str]] = {
    "Accounts": [
        "balance", "statement", "details", "nominees", "kyc-status",
        "dormant-status", "interest-history", "charges", "limits",
        "standing-instructions", "auto-pay", "sweep-rules",
        "tax-certificate", "mini-statement", "profile", "preferences",
        "alerts", "linked-accounts", "savings-goals", "card-link-status",
        "cheque-status", "mandates", "direct-debits", "freeze-status",
        "closure-details", "interest-payments", "tax-withholding",
        "account-opening-status", "cheque-requests", "love-letter",
    ],
    "UPI": [
        "pay", "collect", "validate-vpa", "merchant-qr",
        "mandate", "refund", "transaction-history", "pending-requests",
        "account-mapper", "callback-status", "device-binding",
        "limits", "daily-summary", "dispute", "charge-details",
        "merchant-settlement", "reconciliation", "report",
        "analytics", "health",
    ],
    "NEFT": [
        "transfer", "status", "beneficiary", "validate-account",
        "schedule", "cancel", "limits", "holiday-calendar",
        "charge-details", "bulk-transfer", "summary",
        "transaction-report", "beneficiary-group", "approval-queue",
        "callback", "reconciliation", "hold", "release-hold",
        "search-transactions", "analytics",
    ],
    "IMPS": [
        "payment", "status", "beneficiary", "validate-mmid",
        "validate-mobile", "limits", "charge-check",
        "transaction-history", "cancel", "bulk-payment",
        "reconciliation", "callback", "refund", "dispute",
        "daily-report", "mmid-generation", "mobile-registration",
        "approval-queue", "charge-slab", "analytics",
    ],
    "RTGS": [
        "transfer", "status", "beneficiary", "validate-account",
        "schedule", "limits", "holiday-calendar", "charge-calculator",
        "bulk-transfer", "summary", "approval-queue",
        "callback", "reconciliation", "hold", "release-hold",
        "transaction-report", "beneficiary-group", "daily-report",
        "analytics", "health",
    ],
    "Cards": [
        "transactions", "statement", "block", "replace",
        "limit", "pin-change", "details", "rewards",
        "forex-charges", "emi-options", "apply", "types",
        "lost-report", "dispute", "activation", "hotlist",
        "international-usage", "contactless-limit", "card-status",
        "ecom-limits", "renewal", "upgrade", "statement-pdf",
        "payment-due", "history", "charge-details",
    ],
    "Loans": [
        "statement", "details", "emi-schedule", "foreclosure",
        "documents", "eligibility", "interest-rates",
        "pre-approved", "application-status", "repayment-history",
        "partial-prepayment", "loan-certificate", "insurance-details",
        "collateral-details", "disbursement-status", "npa-status",
        "restructure", "moratorium", "late-fees", "tax-benefit",
    ],
    "KYC": [
        "verify", "status", "document-upload", "details",
        "update", "aadhaar-verify", "pan-verify", "video-initiate",
        "document-types", "digilocker-fetch", "ckyc-status",
        "risk-profile", "periodic-update", "re-kyc",
        "offline-aadhaar", "address-proof", "photo-upload",
        "signature-upload", "nominee-details", "compliance-status",
    ],
    "Forex": [
        "rates", "convert", "travel-card-load", "travel-card-details",
        "remittance", "rates-history", "rate-alert", "limits",
        "calculate", "beneficiary", "transaction-status",
        "travel-card-block", "travel-card-statement",
        "forex-approval", "denomination-calc", "buy-order",
        "sell-order", "rate-notification", "holiday-calendar",
        "analytics",
    ],
    "FixedDeposits": [
        "create", "details", "renewal", "closure",
        "rates", "certificate", "interest-payout",
        "premature-calc", "tax-deduction", "nominee-update",
        "statement", "bulk-create", "fd-tracking",
        "maturity-reminder", "auto-renewal", "part-withdrawal",
        "loan-against-fd", "fd-tds-certificate", "interest-history",
        "cumulative-noncumulative",
    ],
    "RecurringDeposits": [
        "create", "details", "renewal", "closure",
        "rates", "missed-installment", "step-up",
        "standing-instruction", "statement", "interest-calc",
        "premature-calc", "nominee-update", "bulk-create",
        "rd-tracking", "maturity-reminder", "auto-renewal",
        "part-withdrawal", "loan-against-rd", "tds-certificate",
        "interest-history",
    ],
    "Cheque": [
        "status", "stop-payment", "book-request", "inquiry",
        "image", "return-details", "truncation-status",
        "bulk-stop-payment", "leaf-limits", "deposit-status",
        "micr-verify", "cheque-confirm", "positive-pay",
        "cheque-issue", "cheque-cancel", "multi-account-book",
        "cheque-template", "cheque-history", "stop-payment-status",
        "analytics",
    ],
    "Notifications": [
        "email-send", "sms-send", "push-send", "template",
        "schedule", "history", "preferences", "channel-status",
        "bulk-send", "log", "priority-queue", "delivery-report",
        "template-create", "template-approve", "dlt-registration",
        "sender-id", "unicode-support", "attachment-upload",
        "scheduled-bulk", "analytics-dashboard",
    ],
    "Admin": [
        "users", "audit-log", "config", "health", "metrics",
        "feature-flags", "rate-limit-config", "service-registry",
        "users-create", "roles", "permissions", "api-keys",
        "secrets-rotate", "backup-status", "incident-log",
        "deployment-history", "resource-quotas", "maintenance-window",
        "access-requests", "compliance-check",
    ],
    "Reporting": [
        "transactions", "summary", "analytics", "export",
        "compliance", "daily-settlement", "mis-report",
        "audit-trail", "chargebacks", "reconciliation",
        "profit-loss", "balance-sheet", "npa-report",
        "branch-performance", "product-wise", "ageing-report",
        "forex-position", "regulatory-report", "rbi-return",
        "board-report",
    ],
    "AuthGateway": [
        "login", "refresh", "otp-generate", "otp-validate",
        "session-validate", "logout", "mfa-setup",
        "forgot-password", "reset-password", "change-password",
        "device-register", "device-deregister", "biometric-verify",
        "pin-set", "pin-change", "pin-validate",
        "sso-validate", "token-refresh", "session-list",
        "active-sessions",
    ],
    "DigitalWallet": [
        "balance", "add-money", "withdraw", "transactions",
        "link-bank-account", "statement", "send-money",
        "request-money", "wallet-to-bank", "bank-to-wallet",
        "split-payment", "cashback-history", "offer-list",
        "coupon-apply", "reward-points", "qr-code",
        "merchant-pay", "wallet-freeze", "wallet-close",
        "transaction-limits",
    ],
    "ServiceRegistry": [
        "services", "service-details", "discover", "health",
        "register", "deregister", "update-endpoint",
        "dependencies", "circuit-breaker-status", "load-balancer-config",
        "retry-policy", "timeout-config", "rate-limiter",
        "service-map", "dependency-graph", "incident-history",
        "version-info", "bluegreen-status", "canary-status",
        "rollback-history",
    ],
}


def expand_endpoints() -> List[Dict[str, Any]]:
    """
    Expand base domain templates into Union Bank-scale endpoint list (10,000+).
    """
    expanded = []
    for domain in DOMAINS:
        resources = SCALE_RESOURCES.get(domain.name, [])
        for resource in resources:
            for version in domain.versions:
                host = domain.host
                prefix = f"{domain.base_path}/v{version}"

                expanded.append({
                    "host": host, "path": f"{prefix}/{domain.name.lower()}/{resource}",
                    "method": "GET", "domain": domain.name, "version": version,
                    "traffic_level": domain.traffic_level, "param_count": 0,
                })
                if not resource.endswith("-list") and not resource.endswith("-config"):
                    expanded.append({
                        "host": host, "path": f"{prefix}/{domain.name.lower()}/{resource}/{{id}}",
                        "method": "GET", "domain": domain.name, "version": version,
                        "traffic_level": domain.traffic_level, "param_count": 1,
                    })
                if resource not in ("list", "types", "rates", "history", "analytics", "health"):
                    expanded.append({
                        "host": host, "path": f"{prefix}/{domain.name.lower()}/{resource}",
                        "method": "POST", "domain": domain.name, "version": version,
                        "traffic_level": domain.traffic_level, "param_count": 0,
                    })
                if resource.endswith("/update") or resource.endswith("/edit"):
                    expanded.append({
                        "host": host, "path": f"{prefix}/{domain.name.lower()}/{resource}",
                        "method": "PUT", "domain": domain.name, "version": version,
                        "traffic_level": domain.traffic_level, "param_count": 0,
                    })

        for svc_num in range(1, 11):
            for region_suffix in ["", "-dc1", "-dc2"]:
                svc_host = f"{domain.name.lower()}-svc-{svc_num}{region_suffix}.bank.example.com"
                for resource in resources[:40]:
                    for version in domain.versions:
                        path_prefix = f"{domain.base_path}/v{version}"
                        expanded.append({
                            "host": svc_host,
                            "path": f"{path_prefix}/{domain.name.lower()}/{resource}",
                            "method": "GET",
                            "domain": domain.name,
                            "version": version,
                            "traffic_level": domain.traffic_level,
                            "param_count": 0,
                        })
                        if not resource.endswith("-list"):
                            expanded.append({
                                "host": svc_host,
                                "path": f"{path_prefix}/{domain.name.lower()}/{resource}/{{id}}",
                                "method": "GET",
                                "domain": domain.name,
                                "version": version,
                                "traffic_level": domain.traffic_level,
                                "param_count": 1,
                            })
                        # Sub-resource expansions for deeper API surface
                        if svc_num <= 5 and resource not in ("list", "health", "metrics", "analytics"):
                            for sub_res in ["status", "history", "config"]:
                                expanded.append({
                                    "host": svc_host,
                                    "path": f"{path_prefix}/{domain.name.lower()}/{resource}/{{id}}/{sub_res}",
                                    "method": "GET",
                                    "domain": domain.name,
                                    "version": version,
                                    "traffic_level": domain.traffic_level,
                                    "param_count": 1,
                                })

    # Add original domain templates too
    for domain in DOMAINS:
        for version in domain.versions:
            for template in domain.endpoint_templates:
                for method in template["methods"]:
                    path = f"{domain.base_path}/v{version}{template['path']}"
                    expanded.append({
                        "host": domain.host,
                        "path": path,
                        "method": method,
                        "domain": domain.name,
                        "version": version,
                        "traffic_level": domain.traffic_level,
                        "param_count": template["param_count"],
                    })

    return expanded


def generate_endpoints() -> List[Dict[str, Any]]:
    """Generate all endpoints with scale expansion + zombie labeling."""
    rng = random.Random(42)

    # Get expanded endpoint list
    raw_endpoints = expand_endpoints()
    logger.info(f"Raw generated endpoints: {len(raw_endpoints)}")

    # Deduplicate by (host, method, path)
    seen = set()
    endpoints = []
    for ep in raw_endpoints:
        key = (ep["host"], ep["method"], ep["path"])
        if key not in seen:
            seen.add(key)
            endpoints.append(ep)

    # Assign zombie probability and label per endpoint
    for ep in endpoints:
        domain_name = ep["domain"]
        version = ep["version"]
        # Find domain config
        domain_cfg = None
        for d in DOMAINS:
            if d.name == domain_name:
                domain_cfg = d
                break
        if domain_cfg is None:
            continue
        base_rate = domain_cfg.zombie_rate_by_version.get(version, 0.3)
        adjusted_rate = base_rate * domain_cfg.zombie_rate_multiplier
        noise = rng.gauss(0, 0.08)
        zombie_prob = max(0.01, min(0.95, adjusted_rate + noise))
        ep["zombie_prob"] = round(zombie_prob, 4)
        ep["is_zombie"] = rng.random() < zombie_prob

    # Surprise zombies (v2/v3 endpoints that are actually zombie)
    for ep in endpoints:
        if ep["version"] >= 2 and not ep["is_zombie"] and rng.random() < 0.03:
            ep["is_zombie"] = True

    # Surprise actives (v1 endpoints still maintained)
    for ep in endpoints:
        if ep["version"] == 1 and ep["is_zombie"] and rng.random() < 0.08:
            ep["is_zombie"] = False

    zombie_count = sum(1 for e in endpoints if e["is_zombie"])
    active_count = len(endpoints) - zombie_count
    logger.info(f"Generated {len(endpoints)} unique endpoints across {len(DOMAINS)} domains")
    logger.info(f"  Active: {active_count} ({active_count/len(endpoints)*100:.1f}%)")
    logger.info(f"  Zombie: {zombie_count} ({zombie_count/len(endpoints)*100:.1f}%)")
    return endpoints


# ──────────────────────────────────────────────
# FEATURE COMPUTATION
# ──────────────────────────────────────────────

def compute_features(endpoint: Dict[str, Any],
                     rng: random.Random) -> Dict[str, Any]:
    """
    Compute 16 features with HEAVILY overlapping distributions between
    zombie and active endpoints — no single feature can separate the classes.
    The true signal is a combination of many weak trends, forcing XGBoost
    to learn multi-feature interactions.
    """
    is_zombie = endpoint["is_zombie"]
    traffic_level = endpoint["traffic_level"]
    version = endpoint["version"]

    mean_calls, std_calls = traffic_level_to_base_calls(traffic_level)
    version_mult = version_traffic_multiplier(version)

    # ── total_calls ──
    # Both classes share the same base volume; zombie slightly lower on avg
    mu_total = mean_calls * version_mult * (0.90 if is_zombie else 1.0)
    total = int(abs(rng.gauss(mu_total, std_calls)))

    # ── synthetic_ratio (heavily overlapping) ──
    # Zombie: 0.20-0.85, many have real traffic too
    # Active: 0.02-0.55, some are heavily synthetic (monitoring)
    if is_zombie:
        synth_ratio = rng.uniform(0.20, 0.85)
    else:
        synth_ratio = rng.uniform(0.02, 0.55)
    # Add noise so ratio isn't purely class-determined
    synth_ratio = max(0.0, min(1.0, synth_ratio + rng.gauss(0, 0.08)))

    total = max(total, 1)
    synthetic = int(total * synth_ratio)
    real = total - synthetic

    # ── days_since_last_real_call ──
    # Both classes span 0-365 with heavy overlap
    if is_zombie:
        days = max(0, int(rng.gauss(35, 40)))
    else:
        days = max(0, int(rng.gauss(8, 25)))
    days = min(days, 365)

    # ── unique_user_agents ──
    # Both 1-20+, zombie slightly fewer
    if is_zombie:
        ua = max(1, int(abs(rng.gauss(5, 4))))
    else:
        ua = max(1, int(abs(rng.gauss(9, 7))))

    # ── unique_source_ips ──
    if is_zombie:
        ips = max(1, int(abs(rng.gauss(3, 3))))
    else:
        ips = max(1, int(abs(rng.gauss(6, 5))))

    # ── auth_ratio (CRITICAL: must overlap heavily) ──
    # Zombie: 0.15-0.70 (monitoring credentials, stale tokens)
    # Active: 0.35-0.98 (some failures, expired sessions)
    if is_zombie:
        auth = rng.uniform(0.15, 0.70)
    else:
        auth = rng.uniform(0.35, 0.98)
    auth += rng.gauss(0, 0.05)
    auth = max(0.0, min(1.0, auth))

    # ── HTTP status ratios ──
    if is_zombie:
        r2xx = rng.uniform(0.68, 0.99)
    else:
        r2xx = rng.uniform(0.78, 0.99)
    remaining = 1.0 - r2xx
    if is_zombie:
        r4xx = rng.uniform(0.0, remaining)
    else:
        r4xx = rng.uniform(0.01, min(0.20, remaining))
    r5xx = remaining - r4xx

    # ── response_size_mean / stddev (heavily overlapping) ──
    # Both classes span wide ranges with significant overlap
    if is_zombie:
        mean_size = abs(rng.gauss(1800, 1400))
        std_size = rng.uniform(50, 700)
    else:
        mean_size = abs(rng.gauss(2400, 1600))
        std_size = rng.uniform(100, 1000)

    # ── interarrival_mean_ms / stddev ──
    # Both now use similar distributions; zombie slightly more regular
    if is_zombie:
        mean_ia = abs(rng.gauss(25_000, 30_000))
        std_ia = rng.uniform(100, 6_000)
    else:
        mean_ia = abs(rng.gauss(15_000, 20_000))
        std_ia = rng.uniform(1_000, 12_000)
    mean_ia = max(100, mean_ia)

    # ── unique_hours_of_day (heavily overlapping) ──
    if is_zombie:
        hours = rng.randint(2, 20)
    else:
        hours = rng.randint(4, 22)

    # ── is_100pct_synthetic ──
    # Rare in both classes, only slightly more common for zombies
    real_val = real
    is_100pct = (synthetic > 0 and real_val == 0)

    return {
        "total_calls": total,
        "synthetic_calls": synthetic,
        "real_calls": real,
        "days_since_last_real_call": days,
        "unique_user_agents": ua,
        "unique_source_ips": ips,
        "auth_ratio": round(auth, 4),
        "ratio_2xx": round(r2xx, 4),
        "ratio_4xx": round(r4xx, 4),
        "ratio_5xx": round(r5xx, 4),
        "response_size_mean": round(mean_size, 2),
        "response_size_stddev": round(std_size, 2),
        "interarrival_mean_ms": round(mean_ia, 2),
        "interarrival_stddev_ms": round(std_ia, 2),
        "unique_hours_of_day": hours,
        "is_100pct_synthetic": is_100pct,
    }


# ──────────────────────────────────────────────
# COST MODEL
# ──────────────────────────────────────────────

def estimate_annual_cost(endpoint: Dict[str, Any], features: Dict[str, Any]) -> float:
    """
    Estimate annual maintenance cost in INR for an API endpoint.
    Factors: compute, storage, bandwidth, team, compliance.
    """
    is_zombie = endpoint["is_zombie"]
    calls = features["total_calls"]
    level = endpoint["traffic_level"]

    # Base cost per endpoint per year
    base_cost = 50_000  # ₹50K minimum per endpoint

    # Compute cost based on traffic volume
    if level == "critical":
        compute = calls * 0.002  # ₹0.002 per call
    elif level == "high":
        compute = calls * 0.001
    elif level == "moderate":
        compute = calls * 0.0008
    else:
        compute = calls * 0.0005

    # Storage cost (response data)
    storage = features["response_size_mean"] * calls * 0.000001 * 12  # 12 months retention

    # Team cost (assumed fractional FTE per endpoint)
    if is_zombie:
        # Zombies still cost: monitoring, alerting, security scanning
        team_cost = 120_000  # ₹1.2L/year for incidental maintenance
    else:
        team_cost = 300_000  # ₹3L/year for active maintenance

    # Compliance cost (audits, patching, vulnerability scanning)
    compliance = 80_000 if is_zombie else 200_000

    # Security risk cost (zombies have higher risk — unpatched, forgotten)
    risk = 250_000 if is_zombie else 50_000

    total = base_cost + compute + storage + team_cost + compliance + risk
    return round(total, 2)


# ──────────────────────────────────────────────
# MAIN ENTRY POINTS
# ──────────────────────────────────────────────

def generate_feature_data(output_path: str = "demo/test-data/endpoint_features.parquet"):
    """Generate the full feature dataset and write to Parquet."""
    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas required. Run: pip install pandas pyarrow numpy")
        sys.exit(1)

    rng = random.Random(42)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    endpoints = generate_endpoints()
    rows = []
    cost_savings = 0.0

    for ep in endpoints:
        features = compute_features(ep, rng)
        annual_cost = estimate_annual_cost(ep, features)

        if ep["is_zombie"]:
            cost_savings += annual_cost

        # Build param placeholders in path for realism
        path = ep["path"]
        for i in range(ep["param_count"]):
            path = path.replace(f"{{id}}", str(rng.randint(1000, 9999)), 1) if "{id}" in path else \
                   path.replace(f"{{txn_id}}", f"TXN{rng.randint(100000,999999)}", 1) if "{txn_id}" in path else \
                   path.replace(f"{{ref_id}}", f"KYC{rng.randint(10000,99999)}", 1) if "{ref_id}" in path else \
                   path.replace(f"{{name}}", f"svc-{rng.choice(['accounts','payments','cards','loans','auth'])}", 1) if "{name}" in path else \
                   path.replace(f"{{doc_id}}", f"DOC{rng.randint(1000,9999)}", 1) if "{doc_id}" in path else \
                   path.replace(f"{{pair}}", f"USDINR", 1) if "{pair}" in path else \
                   path

                # Replace any remaining {param} patterns
        while "{id}" in path:
            path = path.replace("{id}", str(rng.randint(1000, 9999)), 1)
        while "{txn_id}" in path:
            path = path.replace("{txn_id}", f"TXN{rng.randint(100000,999999)}", 1)
        while "{ref_id}" in path:
            path = path.replace("{ref_id}", f"KYC{rng.randint(10000,99999)}", 1)
        while "{name}" in path:
            path = path.replace("{name}", f"svc-{rng.choice(['accounts','payments','cards','loans','auth'])}", 1)
        while "{doc_id}" in path:
            path = path.replace("{doc_id}", f"DOC{rng.randint(1000,9999)}", 1)
        while "{pair}" in path:
            path = path.replace("{pair}", rng.choice(["USDINR", "EURINR", "GBPINR", "JPYINR"]), 1)
        while "{id}" in path:
            path = path.replace("{id}", str(rng.randint(1000, 9999)), 1)
        while "{i}" in path:
            path = path.replace("{i}", str(rng.randint(1000, 9999)), 1)

        key = f"{ep['host']}|{ep['method']}|{path}"

        row = {
            "endpoint_key": key,
            "host": ep["host"],
            "domain": ep["domain"],
            "api_version": ep["version"],
            "method": ep["method"],
            "path": path,
            "traffic_level": ep["traffic_level"],
            "annual_cost_inr": annual_cost,
            "event_timestamp": pd.Timestamp.now() - pd.Timedelta(days=rng.randint(0, 90)),
            "created_timestamp": pd.Timestamp.now(),
        }

        for feat_name, feat_val in features.items():
            row[feat_name] = feat_val

        row["is_zombie"] = 1 if ep["is_zombie"] else 0
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_parquet(output_path, index=False)
    logger.info(f"Generated {len(df)} rows of feature data -> {output_path}")
    logger.info(f"  Columns: {list(df.columns)}")

    zombie_count = df["is_zombie"].sum()
    active_count = len(df) - zombie_count
    logger.info(f"  Active: {active_count}, Zombie: {zombie_count}")
    logger.info(f"  Zombie rate: {zombie_count/len(df)*100:.1f}%")

    if "annual_cost_inr" in df.columns:
        total_zombie_cost = df[df["is_zombie"] == 1]["annual_cost_inr"].sum()
        total_active_cost = df[df["is_zombie"] == 0]["annual_cost_inr"].sum()
        total_cost = df["annual_cost_inr"].sum()
        logger.info(f"  Annual zombie endpoint cost: INR {total_zombie_cost:,.2f}")
        logger.info(f"  Annual active endpoint cost: INR {total_active_cost:,.2f}")
        logger.info(f"  Total annual API cost: INR {total_cost:,.2f}")
        logger.info(f"  Potential savings (decommission zombies): INR {total_zombie_cost:,.2f}/year")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-features":
        output_path = sys.argv[2] if len(sys.argv) > 2 else "demo/test-data/endpoint_features.parquet"
        generate_feature_data(output_path)
        return

    # Live traffic mode
    logger.info("Starting API traffic simulator")
    endpoints = generate_endpoints()
    rng = random.Random()
    logger.info(f"  Live traffic mode: {len(endpoints)} endpoints")

    while True:
        ep = rng.choice(endpoints)
        features = compute_features(ep, rng)

        # Build a realistic call record
        call = {
            "ts": time.time(),
            "method": ep["method"],
            "path": ep["path"],
            "host": ep["host"],
            "status": 200 if features["ratio_2xx"] > features["ratio_4xx"] else
                      404 if features["ratio_4xx"] > features["ratio_5xx"] else 500,
            "user_agent": rng.choice(REAL_USER_AGENTS if not ep["is_zombie"] else SYNTHETIC_USER_AGENTS),
            "source_ip": rng.choice(REAL_SOURCE_IPS if not ep["is_zombie"] else SYNTHETIC_SOURCE_IPS),
            "response_size": features["response_size_mean"],
            "auth_header": "Bearer <token>" if features["auth_ratio"] > 0.5 else "",
            "is_zombie": ep["is_zombie"],
            "domain": ep["domain"],
            "api_version": ep["version"],
        }
        print(json.dumps(call))
        sys.stdout.flush()

        # Vary sleep time to simulate realistic traffic patterns
        if ep["traffic_level"] == "critical":
            sleep_time = rng.expovariate(10)  # ~100ms avg
        elif ep["traffic_level"] == "high":
            sleep_time = rng.expovariate(3)    # ~300ms avg
        elif ep["traffic_level"] == "moderate":
            sleep_time = rng.expovariate(1)    # ~1s avg
        else:
            sleep_time = rng.expovariate(0.2)  # ~5s avg

        time.sleep(max(0.05, min(sleep_time, 10)))


if __name__ == "__main__":
    main()
