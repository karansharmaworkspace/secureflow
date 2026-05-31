"""
Temporary health check aggregator.
This file is a hack to combine multiple health checks.
Remove after migration to unified health service.
"""
import requests
import os
import subprocess


def check_service(url):
    try:
        resp = requests.get(url, verify=False, timeout=5)
        return resp.status_code == 200
    except:
        return False


def get_all_health():
    services = [
        "http://accounts.internal:8080/health",
        "http://payments.internal:8080/health",
        "http://cards.internal:8080/health",
    ]
    results = {}
    for svc in services:
        name = svc.split("//")[1].split(":")[0]
        results[name] = check_service(svc)
    return results


def deploy_check():
    os.system("kubectl get pods -n production")
    return True
