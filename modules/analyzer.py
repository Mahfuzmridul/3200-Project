import pandas as pd
from collections import Counter
from datetime import datetime, timedelta
from rich import print


def detect_basic_anomalies(df):
    """Detect suspicious patterns in Windows logs with advanced analysis."""
    if df is None or df.empty:
        return ["⚠️ No data available for analysis."]

    findings = []
    findings.append(f"📋 Total Events Analyzed: {len(df)}")
    findings.append("─" * 80)

    # Check data quality first
    valid_event_ids = df[df["EventID"].notna()]
    valid_timestamps = df[df["TimeGenerated"].notna()]
    valid_messages = df[df["Message"].notna() & (df["Message"] != "")]

    if len(valid_event_ids) < len(df) * 0.5:
        findings.append(
            f"⚠️ WARNING: {len(df) - len(valid_event_ids)} events have missing EventID (data quality issue)"
        )

    if len(valid_timestamps) < len(df) * 0.5:
        findings.append(
            f"⚠️ WARNING: {len(df) - len(valid_timestamps)} events have missing timestamps"
        )

    # 1. Failed Login Detection (Brute Force)
    failed_logins = df[
        df["Message"].str.contains("failure|failed|4625", case=False, na=False)
    ]
    if len(failed_logins) > 5:
        findings.append(
            f"🔴 CRITICAL: {len(failed_logins)} failed login attempts detected (possible brute force attack)."
        )

        # Check for repeated attempts from same source
        if len(failed_logins) > 10:
            findings.append(
                f"🔴 HIGH RISK: Excessive failed logins detected - investigate immediately!"
            )

    # 2. Privilege-related Activity
    privilege_events = df[
        df["Message"].str.contains("privilege|admin|elevated", case=False, na=False)
    ]
    if len(privilege_events) > 0:
        findings.append(
            f"⚠️ WARNING: {len(privilege_events)} privilege-related activities detected (potential privilege escalation)."
        )

    # 3. Time-based Anomaly Detection
    try:
        df["TimeGenerated"] = pd.to_datetime(df["TimeGenerated"], errors="coerce")
        df_valid_time = df[df["TimeGenerated"].notna()]

        if not df_valid_time.empty:
            # Check for event spikes
            events_per_min = df_valid_time.groupby(
                df_valid_time["TimeGenerated"].dt.minute
            ).size()
            if len(events_per_min) > 0:
                mean_events = events_per_min.mean()
                max_events = events_per_min.max()
                if max_events > (mean_events * 3):
                    findings.append(
                        f"🔴 ALERT: Sudden spike in event frequency detected (max: {max_events}, avg: {mean_events:.1f})."
                    )

            # Check for unusual time activity (late night/early morning)
            df_valid_time["hour"] = df_valid_time["TimeGenerated"].dt.hour
            unusual_hours = df_valid_time[
                (df_valid_time["hour"] >= 0) & (df_valid_time["hour"] <= 5)
            ]
            if len(unusual_hours) > len(df_valid_time) * 0.3:
                findings.append(
                    f"⚠️ WARNING: {len(unusual_hours)} events during unusual hours (12 AM - 5 AM)."
                )
    except Exception as e:
        findings.append(f"⚠️ Could not perform time-based analysis: {str(e)}")

    # 4. Event ID Analysis (Windows Security Events)
    if "EventID" in df.columns:
        event_counts = Counter(df["EventID"].dropna())

        # Common suspicious Event IDs
        suspicious_events = {
            1102: "Audit Log Cleared (CRITICAL - Evidence Tampering)",
            4624: "Successful Logon",
            4625: "Failed Logon (Potential Brute Force)",
            4648: "Logon Using Explicit Credentials",
            4672: "Special Privileges Assigned (Admin Access)",
            4720: "User Account Created",
            4722: "User Account Enabled",
            4724: "Password Reset Attempt",
            4732: "Member Added to Security Group",
            4756: "Member Added to Universal Security Group",
            4768: "Kerberos Authentication Ticket Requested",
            4769: "Kerberos Service Ticket Requested",
            4776: "NTLM Authentication",
        }

        for event_id, description in suspicious_events.items():
            count = event_counts.get(event_id, 0)
            if count > 0:
                severity = (
                    "🔴 CRITICAL" if event_id in [1102, 4672, 4720, 4724] else "⚠️ INFO"
                )
                findings.append(
                    f"{severity} - Event ID {event_id}: {description} - {count} occurrence(s)"
                )

    # 5. Source Name Analysis
    if "SourceName" in df.columns:
        source_counts = Counter(df[df["SourceName"] != ""]["SourceName"])
        top_sources = source_counts.most_common(5)
        if top_sources:
            findings.append("\n📊 Top Event Sources:")
            for source, count in top_sources:
                findings.append(f"   • {source}: {count} events")

    # 6. Computer/Host Analysis
    if "Computer" in df.columns:
        computers = df[df["Computer"] != ""]["Computer"].unique()
        if len(computers) > 0:
            findings.append(f"\n💻 Affected Systems: {', '.join(computers)}")

    # 7. Security-specific checks
    security_keywords = [
        "malware",
        "virus",
        "trojan",
        "unauthorized",
        "denied",
        "blocked",
        "suspicious",
        "cleared",  # For audit log clearing
        "deleted",
    ]
    for keyword in security_keywords:
        matches = df[df["Message"].str.contains(keyword, case=False, na=False)]
        if len(matches) > 0:
            findings.append(
                f"🔴 SECURITY ALERT: {len(matches)} event(s) containing '{keyword}' detected!"
            )

    # 8. Account lockout detection
    lockout_events = df[
        df["Message"].str.contains("lockout|locked out", case=False, na=False)
    ]
    if len(lockout_events) > 0:
        findings.append(
            f"🔴 CRITICAL: {len(lockout_events)} account lockout events detected!"
        )

    # 9. Privilege escalation detection
    priv_escalation = df[
        df["Message"].str.contains(
            "administrator|admin|elevated|privilege|sudo|runas", case=False, na=False
        )
    ]
    if len(priv_escalation) > 0:
        findings.append(
            f"⚠️ INFO: {len(priv_escalation)} privilege-related events (review for unauthorized escalation)"
        )

    # 10. User and group analysis from messages
    try:
        usernames = []
        for msg in df["Message"].dropna():
            if "UserName" in msg or "SubjectUserName" in msg:
                # Extract username from message
                import re

                user_match = re.search(r"(?:Subject)?UserName: ([^|]+)", str(msg))
                if user_match:
                    usernames.append(user_match.group(1).strip())

        if usernames:
            unique_users = list(set(usernames))[:10]  # Top 10 unique users
            findings.append(
                f"\n👤 Detected Users: {', '.join(unique_users[:5])}{' ...' if len(unique_users) > 5 else ''}"
            )
    except:
        pass

    if len(findings) <= 2:  # Only header and separator
        findings.append("✅ No significant anomalies detected. System appears normal.")

    return findings
