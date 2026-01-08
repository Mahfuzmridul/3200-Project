# Quick Start Guide

## First-Time Setup

1. **Open Terminal as Administrator**

   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Command Prompt (Admin)"

2. **Navigate to project directory**

   ```bash
   cd "E:\RUET\Project 3200\merged_analyzer"
   ```

3. **Activate virtual environment** (if you have one)

   ```bash
   .venv\Scripts\activate
   ```

4. **Install/Update dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

**Always run as Administrator for full functionality:**

```bash
python main.py
```

## Quick Test

### Test Log Analysis

1. Run the application
2. Select option 1 (Automatic Windows Log Analysis)
3. Wait for analysis to complete
4. Check `reports/` folder for generated reports

### Test File Analysis

1. Copy a `.evtx` file to the `user_logs/` folder
2. Run the application
3. Select option 2
4. Choose your file
5. View results in `reports/` folder

## Common Issues

### "Access Denied"

- **Solution**: Run as Administrator (required for Windows Security logs)

### "Module not found"

- **Solution**: Run `pip install -r requirements.txt`

### "No interfaces found" (PCAP)

- **Solution**: Install Npcap from https://npcap.com/

### Rich formatting not working

- **Solution**: Use Windows Terminal or modern terminal emulator

## Output Files

All reports are saved in the `reports/` directory:

- `*.json` - Structured data
- `*.csv` - Spreadsheet format
- `*_summary.txt` - Text report
- `*_report.html` - Interactive web report

## Tips

1. **Large log files**: Increase `MAX_EVENTS` in `config.py`
2. **Custom analysis**: Modify thresholds in `config.py`
3. **Network capture**: Requires Npcap/WinPcap installed
4. **View HTML reports**: Open `.html` files in any web browser

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the `modules/` folder to understand the code structure
- Customize `config.py` for your specific needs
- Contribute improvements via pull requests

---

Need help? Create an issue on GitHub or check the troubleshooting section in README.md
