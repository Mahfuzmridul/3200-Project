# Unified Log & PCAP Analyzer v2.0

A comprehensive Windows Event Log and Network Traffic Analysis tool with advanced anomaly detection capabilities and **AI-powered security analysis**.

## 🌟 Features

### Windows Event Log Analysis

- **Live System Analysis**: Collect and analyze logs directly from Windows Event Log
- **File-Based Analysis**: Support for `.evtx`, `.csv`, and `.json` log files
- **Advanced Anomaly Detection**:
  - Failed login attempts (Brute force detection)
  - Privilege escalation attempts
  - Time-based anomaly detection
  - Event frequency spike detection
  - Account lockout detection
  - Security keyword scanning
  - Windows Event ID analysis

### 🤖 AI-Powered Analysis (NEW!)

- **Automated Incident Analysis**: AI analyzes your security findings and provides detailed reports
- **Remediation Guidance**: Step-by-step actions to fix security issues
- **Multiple AI Providers**:
  - OpenAI (GPT-4) - Best quality
  - Anthropic (Claude) - Detailed analysis
  - Google Gemini - FREE option
  - Ollama - 100% local, private, FREE
- **Comprehensive Reports**:
  - What happened (incident summary)
  - Severity assessment
  - Attack timeline
  - Immediate actions to take
  - Short/medium/long-term remediation steps
  - Prevention measures

See [AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md) for setup instructions.

### Network Traffic Analysis (PCAP)

- Network interface selection and management
- Packet capture functionality
- PCAP file upload and management
- Support for `.pcap` and `.pcapng` formats

### Reporting

- **Multiple Export Formats**:
  - JSON (structured data)
  - CSV (spreadsheet-compatible)
  - TXT (summary report)
  - HTML (interactive web report)
- Rich console output with color-coded findings
- Detailed security findings with severity levels

## 📋 Requirements

- Windows OS (for Windows Event Log access)
- Python 3.8 or higher
- Administrator privileges (required for live log collection)

## 🚀 Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📦 Dependencies

- `pandas` - Data manipulation and analysis
- `python-evtx` - Windows Event Log parsing
- `pywin32` - Windows API access
- `rich` - Enhanced console output
- `scapy` - Network packet manipulation
- `pyshark` - Packet analysis
- `numpy` - Numerical operations
- **AI Libraries (Optional)**:
  - `openai` - For GPT models (recommended)
  - `anthropic` - For Claude models
  - `google-generativeai` - For Gemini (FREE)
  - Ollama - Local AI (no library needed)
- Other dependencies listed in `requirements.txt`

## 💻 Usage

### Running the Application

**Run as Administrator** (required for live log collection):

```bash
python main.py
```

### Main Menu Options

1. **Automatic Windows Log Analysis (Live System)**

   - Collects logs directly from Windows Event Log
   - Requires Administrator privileges
   - Analyzes Security logs by default
   - Generates comprehensive reports
   - **Optional**: AI-powered analysis and remediation guidance

2. **Analyze a Log File**

   - Place your log files in the `user_logs/` directory
   - Supported formats: `.evtx`, `.csv`, `.json`
   - Select file from interactive menu
   - Generates analysis reports
   - **Optional**: AI-powered analysis and remediation guidance

3. **PCAP Tools**

   - List uploaded PCAP files
   - Upload new PCAP files
   - Delete PCAP files
   - Select network interface
   - Start packet capture

4. **View Reports Directory**

   - Browse generated reports
   - View file sizes

5. **Exit**
   - Safely exit the application

## 📁 Directory Structure

```
merged_analyzer/
├── main.py                  # Main application entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── AI_SETUP_GUIDE.md       # AI analysis setup instructions (NEW!)
├── .env.example            # Example environment variables for AI
├── .gitignore             # Git ignore rules
├── modules/               # Core modules
│   ├── analyzer.py        # Anomaly detection logic
│   ├── ai_analyzer.py     # AI-powered analysis (NEW!)
│   ├── file_parser.py     # Log file parsing
│   ├── log_collector.py   # Windows log collection
│   ├── Pcap_builder.py    # Network interface management
│   ├── pcap_uploader.py   # PCAP file management
│   ├── thsark_analyze.py  # Tshark analysis (optional)
│   └── utils.py           # Utility functions
├── reports/               # Generated reports (includes AI analysis)
├── user_logs/             # User-provided log files
├── upload/                # Uploaded PCAP files
├── analyze/               # Analysis workspace
├── tshirk_upload/         # Tshark uploads
└── logs/                  # Application logs
```

## 🔍 Analysis Features

### Security Event Detection

The analyzer automatically detects:

- **🔴 Critical Events**:

  - Excessive failed login attempts (>10)
  - Account lockout events
  - Security keyword matches (malware, virus, etc.)

- **⚠️ Warnings**:

  - Failed login attempts (>5)
  - Privilege escalation attempts
  - Event frequency spikes
  - Unusual time activity (12 AM - 5 AM)

- **📊 Informational**:
  - Top event sources
  - Event ID statistics
  - Total events analyzed

### Windows Event IDs Monitored

- `4624` - Successful Logon
- `4625` - Failed Logon
- `4672` - Special Privileges Assigned
- `4720` - User Account Created
- `4722` - User Account Enabled
- `4724` - Password Reset Attempt
- `4732` - Member Added to Security Group
- `4756` - Member Added to Universal Security Group

## 📊 Output Reports

### JSON Report

Structured data suitable for further processing or integration with other tools.

### CSV Report

Spreadsheet-compatible format for data analysis in Excel or similar tools.

### Text Summary

Human-readable summary of security findings with timestamps.

### HTML Report

Interactive web-based report with:

- Color-coded findings
- Severity indicators
- Data tables
- Professional styling

## ⚙️ Configuration

Edit `config.py` to customize:

```python
DEFAULT_LOG_TYPE = "Security"  # Log type to collect
MAX_EVENTS = 500               # Maximum events to collect
```

Available directories are automatically configured:

- `REPORT_DIR` - Report output location
- `USER_LOG_DIR` - User log file input
- `UPLOAD_DIR` - PCAP file uploads

## 🛡️ Security Considerations

1. **Administrator Privileges**: Required for accessing Windows Security logs
2. **Data Privacy**: Reports may contain sensitive system information
3. **File Permissions**: Ensure proper file permissions on report directories
4. **Network Capture**: Packet capture may require special permissions

## 🐛 Troubleshooting

### "Access is denied" Error

- Run the application as Administrator
- Right-click on Command Prompt/PowerShell → "Run as Administrator"

### "No logs collected"

- Verify you have Administrator privileges
- Check that the log type exists on your system
- Try a different log type (Application, System)

### "No interfaces found" (PCAP)

- Ensure Scapy is properly installed
- Install Npcap (required for Windows packet capture)
- Check network adapter drivers

### Missing Dependencies

```bash
pip install -r requirements.txt --upgrade
```

## 🔄 Updates and Improvements

Version 2.0 includes:

- ✅ Enhanced error handling throughout
- ✅ Progress indicators for long operations
- ✅ Multiple export formats (JSON, CSV, TXT, HTML)
- ✅ Advanced anomaly detection algorithms
- ✅ Improved XML parsing for EVTX files
- ✅ Better user interface with Rich library
- ✅ Comprehensive input validation
- ✅ Network packet capture capabilities
- ✅ Support for multiple log formats

## 📝 License

This project is provided as-is for educational and security analysis purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Support

For issues or questions, please create an issue in the repository.

## ⚠️ Disclaimer

This tool is for legitimate security analysis and monitoring purposes only. Always ensure you have proper authorization before analyzing system logs or capturing network traffic.

---

**Made with ❤️ for Security Professionals**
