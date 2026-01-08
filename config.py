"""
Configuration file for Unified Log & PCAP Analyzer
Modify these settings to customize the application behavior.
"""

import os

# Base directory (automatically detected)
BASE_DIR = os.getcwd()

# Directory paths
REPORT_DIR = os.path.join(BASE_DIR, "reports")
USER_LOG_DIR = os.path.join(BASE_DIR, "user_logs")
UPLOAD_DIR = os.path.join(BASE_DIR, "upload")

# Windows Event Log settings
DEFAULT_LOG_TYPE = "Security"  # Options: Security, Application, System, Setup
MAX_EVENTS = 500  # Maximum number of events to collect (increase for larger analysis)

# Analysis thresholds
FAILED_LOGIN_THRESHOLD = 5  # Number of failed logins to trigger warning
CRITICAL_LOGIN_THRESHOLD = 10  # Number of failed logins to trigger critical alert
EVENT_SPIKE_MULTIPLIER = (
    3  # Event frequency must be this many times average to trigger alert
)

# Report settings
ENABLE_JSON_EXPORT = True
ENABLE_CSV_EXPORT = True
ENABLE_TXT_EXPORT = True
ENABLE_HTML_EXPORT = True

# PCAP settings
DEFAULT_CAPTURE_DURATION = 60  # Default packet capture duration in seconds
MAX_PCAP_FILE_SIZE_MB = 100  # Maximum PCAP file size to upload (in MB)

# AI Analysis settings
AI_ANALYSIS_ENABLED = True  # Enable/disable AI-powered analysis
AI_MAX_TOKENS = 2000  # Maximum tokens for AI response
AI_TEMPERATURE = 0.7  # AI response creativity (0.0-1.0)
