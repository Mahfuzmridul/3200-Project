"""
Automatic PCAP Analysis Module
Generates comprehensive reports from PCAP files without manual interaction.
"""

import os
import subprocess
from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def check_tshark_installed() -> bool:
    """Check if tshark is installed."""
    try:
        result = subprocess.run(
            ["tshark", "--version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_basic_stats(pcap_file: str) -> Dict[str, Any]:
    """Get basic statistics from PCAP file."""
    stats = {
        "file_name": os.path.basename(pcap_file),
        "file_size": os.path.getsize(pcap_file),
        "packet_count": 0,
        "start_time": "",
        "end_time": "",
        "duration": "",
    }

    try:
        # Get packet count and timing
        cmd = ["tshark", "-r", pcap_file, "-q", "-z", "io,stat,0"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )

        if result.stdout:
            for line in result.stdout.split("\n"):
                if "frames" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "frames" in part.lower() and i > 0:
                            try:
                                stats["packet_count"] = int(parts[i - 1])
                            except ValueError:
                                pass
                if "first packet" in line.lower():
                    stats["start_time"] = (
                        line.split(":", 1)[1].strip() if ":" in line else ""
                    )
                if "last packet" in line.lower():
                    stats["end_time"] = (
                        line.split(":", 1)[1].strip() if ":" in line else ""
                    )
    except Exception as e:
        console.print(f"[yellow]Warning: Could not get basic stats: {e}[/yellow]")

    return stats


def get_protocol_hierarchy(pcap_file: str) -> List[Dict[str, Any]]:
    """Get protocol hierarchy statistics."""
    protocols = []

    try:
        cmd = ["tshark", "-r", pcap_file, "-q", "-z", "io,phs"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )

        if result.stdout:
            in_data = False
            for line in result.stdout.split("\n"):
                if "Protocol Hierarchy Statistics" in line:
                    in_data = True
                    continue
                if in_data and line.strip() and not line.startswith("="):
                    parts = line.split()
                    if len(parts) >= 2:
                        protocols.append(
                            {
                                "protocol": parts[0].strip(),
                                "frames": parts[1] if len(parts) > 1 else "0",
                            }
                        )
    except Exception as e:
        console.print(
            f"[yellow]Warning: Could not get protocol hierarchy: {e}[/yellow]"
        )

    return protocols


def get_endpoints(pcap_file: str) -> Dict[str, List[str]]:
    """Get IP endpoints."""
    endpoints = {"ipv4": [], "ipv6": []}

    try:
        cmd = ["tshark", "-r", pcap_file, "-q", "-z", "endpoints,ip"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )

        if result.stdout:
            for line in result.stdout.split("\n"):
                if line.strip() and not line.startswith("=") and "." in line:
                    parts = line.split()
                    if parts:
                        ip = parts[0].strip()
                        if ip and ip[0].isdigit():
                            endpoints["ipv4"].append(ip)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not get endpoints: {e}[/yellow]")

    return endpoints


def get_http_summary(pcap_file: str) -> Dict[str, Any]:
    """Get HTTP traffic summary."""
    http_data = {"requests": [], "total_requests": 0, "methods": {}, "status_codes": {}}

    try:
        # HTTP requests
        cmd = [
            "tshark",
            "-r",
            pcap_file,
            "-Y",
            "http.request",
            "-T",
            "fields",
            "-e",
            "http.request.method",
            "-e",
            "http.host",
            "-e",
            "http.request.uri",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )

        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        method = parts[0]
                        host = parts[1]
                        uri = parts[2]
                        http_data["requests"].append(
                            {"method": method, "host": host, "uri": uri}
                        )
                        http_data["methods"][method] = (
                            http_data["methods"].get(method, 0) + 1
                        )

        http_data["total_requests"] = len(http_data["requests"])

    except Exception as e:
        console.print(f"[yellow]Warning: Could not get HTTP summary: {e}[/yellow]")

    return http_data


def get_dns_queries(pcap_file: str) -> List[str]:
    """Get DNS queries."""
    queries = []

    try:
        cmd = [
            "tshark",
            "-r",
            pcap_file,
            "-Y",
            "dns.qry.name",
            "-T",
            "fields",
            "-e",
            "dns.qry.name",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )

        if result.stdout:
            queries = [
                q.strip() for q in result.stdout.strip().split("\n") if q.strip()
            ]
            queries = list(set(queries))[:50]  # Unique, limit to 50
    except Exception as e:
        console.print(f"[yellow]Warning: Could not get DNS queries: {e}[/yellow]")

    return queries


def detect_security_issues(pcap_file: str) -> List[str]:
    """Detect potential security issues."""
    issues = []

    try:
        # Check for unencrypted protocols
        sensitive_protocols = {
            "http": "Unencrypted HTTP traffic detected",
            "ftp": "Unencrypted FTP traffic detected",
            "telnet": "Unencrypted Telnet traffic detected",
            "smtp and not tls": "Unencrypted SMTP traffic detected",
        }

        for protocol, message in sensitive_protocols.items():
            cmd = ["tshark", "-r", pcap_file, "-Y", protocol, "-c", "1"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                issues.append(f"⚠️ {message}")

        # Check for suspicious ports
        suspicious_ports = [
            ("tcp.port == 4444", "Metasploit default port (4444) detected"),
            ("tcp.port == 31337", "Back Orifice trojan port (31337) detected"),
            ("tcp.port == 12345", "NetBus trojan port (12345) detected"),
            ("tcp.port == 6667", "IRC port (6667) - potential botnet C&C"),
            ("tcp.port == 1337", "LEET port (1337) - potential backdoor"),
        ]

        for filter_exp, message in suspicious_ports:
            cmd = ["tshark", "-r", pcap_file, "-Y", filter_exp, "-c", "1"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                issues.append(f"🔴 {message}")

    except Exception as e:
        console.print(f"[yellow]Warning: Security check incomplete: {e}[/yellow]")

    if not issues:
        issues.append("✅ No obvious security issues detected")

    return issues


def get_tls_info(pcap_file: str) -> Dict[str, Any]:
    """Analyze TLS/SSL traffic."""
    tls_data = {
        "total_connections": 0,
        "versions": {},
        "cipher_suites": [],
        "server_names": [],
    }

    try:
        # TLS versions
        cmd = [
            "tshark",
            "-r",
            pcap_file,
            "-Y",
            "tls.handshake.type == 1",
            "-T",
            "fields",
            "-e",
            "tls.handshake.version",
            "-e",
            "tls.handshake.extensions_server_name",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )

        if result.stdout:
            lines = result.stdout.strip().split("\n")
            tls_data["total_connections"] = len([l for l in lines if l.strip()])

            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if parts[0]:
                        version = parts[0].strip()
                        tls_data["versions"][version] = (
                            tls_data["versions"].get(version, 0) + 1
                        )
                    if len(parts) > 1 and parts[1]:
                        sni = parts[1].strip()
                        if sni and sni not in tls_data["server_names"]:
                            tls_data["server_names"].append(sni)

    except Exception as e:
        console.print(f"[yellow]Warning: Could not analyze TLS: {e}[/yellow]")

    return tls_data


def get_top_talkers(pcap_file: str) -> List[Dict[str, Any]]:
    """Get top talking hosts by packet count."""
    talkers = []

    try:
        cmd = ["tshark", "-r", pcap_file, "-q", "-z", "conv,ip"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )

        if result.stdout:
            in_data = False
            for line in result.stdout.split("\n"):
                if "<->" in line:
                    in_data = True
                if in_data and "<->" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        try:
                            talkers.append(
                                {
                                    "src": parts[0],
                                    "dst": parts[2],
                                    "packets": int(parts[3]),
                                    "bytes": int(parts[4]),
                                }
                            )
                        except (ValueError, IndexError):
                            pass

            # Sort by packet count
            talkers.sort(key=lambda x: x["packets"], reverse=True)

    except Exception as e:
        console.print(f"[yellow]Warning: Could not get top talkers: {e}[/yellow]")

    return talkers[:10]  # Top 10


def get_suspicious_patterns(pcap_file: str) -> List[str]:
    """Detect suspicious network patterns."""
    patterns = []

    checks = [
        (
            "icmp and data.len > 48",
            "⚠️ Large ICMP packets detected (potential data exfiltration)",
        ),
        (
            'dns.qry.name contains "exe" or dns.qry.name contains "dll"',
            "⚠️ Suspicious DNS queries for executables",
        ),
        (
            "tcp.flags.syn == 1 and tcp.flags.ack == 0",
            "🔍 SYN packets detected (potential port scanning)",
        ),
        (
            'http.request.method == "POST" and http.file_data contains "password"',
            "🔴 Potential password in HTTP POST",
        ),
    ]

    try:
        for filter_exp, message in checks:
            cmd = ["tshark", "-r", pcap_file, "-Y", filter_exp, "-c", "5"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=15,
            )
            if result.returncode == 0 and result.stdout.strip():
                count = len(result.stdout.strip().split("\n"))
                patterns.append(f"{message} ({count}+ occurrences)")

    except Exception as e:
        console.print(f"[yellow]Warning: Pattern detection incomplete: {e}[/yellow]")

    return patterns


def generate_report(pcap_file: str, output_dir: str) -> str:
    """Generate comprehensive PCAP analysis report."""

    if not check_tshark_installed():
        console.print("[bold red]Tshark is not installed![/bold red]")
        console.print(
            "[yellow]Please install Wireshark from: https://www.wireshark.org/[/yellow]"
        )
        return None

    console.print("\n[bold cyan]═══ Automatic PCAP Analysis ═══[/bold cyan]")
    console.print(f"[dim]Analyzing: {os.path.basename(pcap_file)}[/dim]\n")

    report_lines = []

    # Header
    report_lines.append("=" * 80)
    report_lines.append("PCAP ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Analyzer: Unified Log & PCAP Analyzer v2.0")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Basic Statistics
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Collecting basic statistics...", total=None)
        stats = get_basic_stats(pcap_file)
        progress.update(task, completed=True)

    report_lines.append("📊 BASIC STATISTICS")
    report_lines.append("-" * 80)
    report_lines.append(f"File Name      : {stats['file_name']}")
    report_lines.append(f"File Size      : {stats['file_size'] / 1024:.2f} KB")
    report_lines.append(f"Packet Count   : {stats['packet_count']}")
    report_lines.append(f"Start Time     : {stats.get('start_time', 'N/A')}")
    report_lines.append(f"End Time       : {stats.get('end_time', 'N/A')}")
    report_lines.append("")

    # Protocol Hierarchy
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Analyzing protocol hierarchy...", total=None)
        protocols = get_protocol_hierarchy(pcap_file)
        progress.update(task, completed=True)

    report_lines.append("🌐 PROTOCOL HIERARCHY")
    report_lines.append("-" * 80)
    if protocols:
        for proto in protocols[:20]:  # Top 20
            report_lines.append(f"  • {proto['protocol']}: {proto['frames']} frames")
    else:
        report_lines.append("  No protocol data available")
    report_lines.append("")

    # Endpoints
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Extracting IP endpoints...", total=None)
        endpoints = get_endpoints(pcap_file)
        progress.update(task, completed=True)

    report_lines.append("🖥️  IP ENDPOINTS")
    report_lines.append("-" * 80)
    if endpoints["ipv4"]:
        report_lines.append(f"Total IPv4 addresses: {len(endpoints['ipv4'])}")
        report_lines.append("Top 10 IPv4 addresses:")
        for ip in endpoints["ipv4"][:10]:
            report_lines.append(f"  • {ip}")
    else:
        report_lines.append("  No IP endpoints found")
    report_lines.append("")

    # HTTP Analysis
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Analyzing HTTP traffic...", total=None)
        http_data = get_http_summary(pcap_file)
        progress.update(task, completed=True)

    report_lines.append("🌍 HTTP TRAFFIC ANALYSIS")
    report_lines.append("-" * 80)
    report_lines.append(f"Total HTTP Requests: {http_data['total_requests']}")
    if http_data["methods"]:
        report_lines.append("\nHTTP Methods:")
        for method, count in http_data["methods"].items():
            report_lines.append(f"  • {method}: {count}")
    if http_data["requests"]:
        report_lines.append("\nSample HTTP Requests (first 10):")
        for req in http_data["requests"][:10]:
            report_lines.append(f"  • {req['method']} {req['host']}{req['uri']}")
    report_lines.append("")

    # DNS Queries
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Extracting DNS queries...", total=None)
        dns_queries = get_dns_queries(pcap_file)
        progress.update(task, completed=True)

    report_lines.append("🔍 DNS QUERIES")
    report_lines.append("-" * 80)
    if dns_queries:
        report_lines.append(f"Total unique queries: {len(dns_queries)}")
        report_lines.append("\nDomain queries:")
        for query in dns_queries[:20]:
            report_lines.append(f"  • {query}")
    else:
        report_lines.append("  No DNS queries found")
    report_lines.append("")

    # Security Issues
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Checking for security issues...", total=None)
        issues = detect_security_issues(pcap_file)
        progress.update(task, completed=True)

    report_lines.append("🔒 SECURITY FINDINGS")
    report_lines.append("-" * 80)
    for issue in issues:
        report_lines.append(f"  {issue}")
    report_lines.append("")

    # TLS/SSL Analysis
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Analyzing TLS/SSL traffic...", total=None)
        tls_data = get_tls_info(pcap_file)
        progress.update(task, completed=True)

    report_lines.append("🔐 TLS/SSL ANALYSIS")
    report_lines.append("-" * 80)
    report_lines.append(f"Total TLS Connections: {tls_data['total_connections']}")
    if tls_data["versions"]:
        report_lines.append("\nTLS Versions:")
        for version, count in tls_data["versions"].items():
            report_lines.append(f"  • {version}: {count} connections")
    if tls_data["server_names"]:
        report_lines.append(
            f"\nTLS Server Names (SNI) - {len(tls_data['server_names'])} unique:"
        )
        for sni in tls_data["server_names"][:15]:
            report_lines.append(f"  • {sni}")
    report_lines.append("")

    # Top Talkers
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Identifying top talkers...", total=None)
        talkers = get_top_talkers(pcap_file)
        progress.update(task, completed=True)

    report_lines.append("💬 TOP CONVERSATIONS")
    report_lines.append("-" * 80)
    if talkers:
        report_lines.append("Source IP → Destination IP | Packets | Bytes")
        report_lines.append("-" * 80)
        for talker in talkers:
            report_lines.append(
                f"  {talker['src']} → {talker['dst']} | {talker['packets']} pkts | {talker['bytes']:,} bytes"
            )
    else:
        report_lines.append("  No conversation data available")
    report_lines.append("")

    # Suspicious Patterns
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task("[cyan]Detecting suspicious patterns...", total=None)
        patterns = get_suspicious_patterns(pcap_file)
        progress.update(task, completed=True)

    if patterns:
        report_lines.append("⚡ SUSPICIOUS PATTERNS DETECTED")
        report_lines.append("-" * 80)
        for pattern in patterns:
            report_lines.append(f"  {pattern}")
        report_lines.append("")

    # Footer
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)

    # Save report with sequential numbering
    from modules.report_numbering import get_report_filename

    report_file, report_num = get_report_filename(
        output_dir, "pcap_analysis", ".txt", is_ai=False
    )

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    # Display report
    console.print("\n[bold green]═══ Analysis Complete ═══[/bold green]\n")
    for line in report_lines:
        print(line)

    console.print(f"\n[bold cyan]📄 Report saved to: {report_file}[/bold cyan]")

    return report_file, report_num
