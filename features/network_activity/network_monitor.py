# features/network_activity/network_monitor.py

import psutil
import socket
import datetime
import re
from urllib.parse import urlparse
from features.network_activity.site_semantic_evaluator import evaluate_multiple_sites

# Списки для детекции
WEBMAIL_DOMAINS = [
    "mail.ru", "gmail.com", "yandex.ru", "outlook.com", "rambler.ru", "icloud.com",
    "protonmail.com", "zoho.com", "gmx.com", "aol.com"
]
FILE_SHARING_DOMAINS = [
    "dropbox.com", "drive.google.com", "disk.yandex.ru", "mega.nz", "fex.net",
    "cloud.mail.ru", "wetransfer.com", "sendspace.com", "files.fm", "1fichier.com"
]
SUSPICIOUS_KEYWORDS = ["взлом", "пароль", "bypass", "adminpanel"]
RISKY_CATEGORIES = ["webmail", "fileshare", "vpn", "proxy", "darknet"]
VPN_PROCESSES = ["openvpn.exe", "nordvpn.exe", "expressvpn.exe", "openvpn"]
PROXY_PORTS = [8080, 3128, 1080, 8000, 8888]
FTP_SMTP_PORTS = [21, 25, 587]

_state = {
    "visited_webmail_allowed": 0,
    "visited_file_sharing_allowed": 0,
    "http_requests_count": 0,
    "upload_volume_MB": 0.0,
    "distinct_domains_accessed": 0,
    "visited_webmail": 0,
    "visited_file_sharing_site": 0,
    "vpn_activated": 0,
    "proxy_used": 0,
    "external_ip_contacted": 0,
    "site_contains_sensitive_words": 0,
    "dns_request_count": 0,
    "suspicious_dns_queries": 0,
    "non_http_traffic_count": 0,
    "used_ftp_or_smtp": 0,
    "upload_spike_detected": 0,
    "visited_risky_category_sites": 0,
    "site_category_diversity": 0,
    "external_upload_without_web_activity": 0,
    "site_semantic_risk_score": 0.0
}

_seen_domains = set()
_categories = set()
_last_sent_bytes = 0


def collect_network_features():
    reset_state()

    global _last_sent_bytes
    counters = psutil.net_io_counters()
    sent = counters.bytes_sent
    recv = counters.bytes_recv

    upload_diff = sent - _last_sent_bytes if _last_sent_bytes else 0
    _last_sent_bytes = sent

    _state["upload_volume_MB"] = round(upload_diff / 1024 / 1024, 2)
    if _state["upload_volume_MB"] > 10:
        _state["upload_spike_detected"] = 1

    connections = psutil.net_connections(kind="inet")
    external_ips = set()
    risky_count = 0
    domains_for_semantic = set()

    for conn in connections:
        if conn.raddr:
            ip = conn.raddr.ip
            port = conn.raddr.port
            try:
                host = socket.gethostbyaddr(ip)[0]
                parts = host.lower().split('.')
                domain = ".".join(parts[-2:]) if len(parts) >= 2 else host
            except:
                domain = ip

            if domain not in _seen_domains:
                _seen_domains.add(domain)
            if domain in WEBMAIL_DOMAINS:
                if domain not in _seen_domains:
                    _state["visited_webmail_allowed"] += 1
                _state["visited_webmail"] += 1
                _categories.add("webmail")
            if domain in FILE_SHARING_DOMAINS:
                if domain not in _seen_domains:
                    _state["visited_file_sharing_allowed"] += 1
                _state["visited_file_sharing_site"] += 1
                _categories.add("fileshare")
            if any(word in domain for word in SUSPICIOUS_KEYWORDS):
                _state["site_contains_sensitive_words"] += 1
            if any(cat in domain for cat in ["vpn", "proxy"]):
                risky_count += 1
                _categories.add("vpn" if "vpn" in domain else "proxy")

            if port not in [80, 443]:
                _state["non_http_traffic_count"] += 1
            if port in FTP_SMTP_PORTS:
                _state["used_ftp_or_smtp"] = 1
            if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", ip):
                external_ips.add(ip)
            if port in PROXY_PORTS:
                _state["proxy_used"] = 1

            _state["http_requests_count"] += 1

            # Запомним только уникальные HTTP-домены
            if port in [80, 443] and re.match(r"[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}$", domain):
                domains_for_semantic.add(f"http://{domain}")

    _state["distinct_domains_accessed"] = len(_seen_domains)
    _state["external_ip_contacted"] = len(external_ips)
    _state["visited_risky_category_sites"] = risky_count
    _state["site_category_diversity"] = len(_categories)

    # DNS (эмуляция счётчика)
    _state["dns_request_count"] = len(_seen_domains) + risky_count
    _state["suspicious_dns_queries"] = 1 if risky_count > 0 else 0

    # VPN процессы
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() in VPN_PROCESSES:
                _state["vpn_activated"] = 1
        except:
            continue

    # Вывод без браузера
    if _state["upload_volume_MB"] > 2 and _state["http_requests_count"] < 3:
        _state["external_upload_without_web_activity"] = 1

    # Семантический анализ сайтов
    if domains_for_semantic:
        result = evaluate_multiple_sites(list(domains_for_semantic))
        _state["site_semantic_risk_score"] = result["site_semantic_risk_score"]

    return dict(_state)


def reset_state():
    for key in _state:
        _state[key] = 0 if isinstance(_state[key], (int, float)) else 0
    _seen_domains.clear()
    _categories.clear()
