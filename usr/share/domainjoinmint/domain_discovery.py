import os
import re
import socket
import subprocess


def _normalize_domain(value):
    if not value:
        return None

    domain = value.strip().strip('.').lower()
    if not domain:
        return None

    if domain.startswith('ldap://') or domain.startswith('ldaps://'):
        domain = domain.split('://', 1)[1]
        domain = domain.split('/', 1)[0]

    if domain.startswith('dns://'):
        domain = domain.split('://', 1)[1]

    if re.match(r'^[a-z0-9.-]+$', domain) is None:
        return None

    if '.' not in domain:
        domain = f"{domain}.local"

    return domain


def build_discovery_message(result):
    if result.stdout and result.stdout.strip():
        return result.stdout.strip()
    if result.stderr and result.stderr.strip():
        return result.stderr.strip()
    return "No domains found."


def collect_discovery_candidates(resolv_conf_path='/etc/resolv.conf', hostname=None):
    domains = []
    seen = set()

    def add_domain(value):
        domain = _normalize_domain(value)
        if domain and domain not in seen:
            seen.add(domain)
            domains.append(domain)

    if os.path.exists(resolv_conf_path):
        try:
            with open(resolv_conf_path, 'r', encoding='utf-8') as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if line.startswith('search'):
                        for part in line.split()[1:]:
                            add_domain(part)
                    elif line.startswith('domain'):
                        add_domain(line.split(maxsplit=1)[1])
        except OSError:
            pass

    if hostname is None:
        try:
            hostname = socket.gethostname()
        except OSError:
            hostname = ''

    if hostname:
        hostname = hostname.strip().lower().rstrip('.')
        if '.' in hostname:
            add_domain(hostname.split('.', 1)[1])
            add_domain(hostname)
        elif hostname:
            add_domain(f'{hostname}.local')

    return domains


def discover_domains(resolv_conf_path='/etc/resolv.conf', hostname=None):
    try:
        result = subprocess.run(['realm', 'discover'], capture_output=True, text=True)
    except FileNotFoundError:
        result = type('Result', (), {'stdout': '', 'stderr': 'realm command not available', 'returncode': 1})()

    if result.returncode == 0 and result.stdout and result.stdout.strip():
        return [line.strip() for line in result.stdout.splitlines() if line.strip()], build_discovery_message(result)

    candidates = collect_discovery_candidates(resolv_conf_path=resolv_conf_path, hostname=hostname)
    if candidates:
        return candidates, 'realm discover did not return a domain; using local DNS search domains.'

    return [], build_discovery_message(result)
