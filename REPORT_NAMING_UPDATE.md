# Report Naming and Organization Update

## Changes Implemented (December 26, 2025)

### Overview

Updated the entire reporting system to use sequential numbering (report_1, report_2, ai_report_1, ai_report_2) instead of timestamps, and organized reports into proper subdirectories with AI reports saved alongside their main reports.

---

## 1. New Report Naming Convention

### Old System (Timestamp-based):

```
reports/
  windows_logs.csv
  windows_logs.json
  analysis_summary.txt
  analysis_report.html
  ai_analysis_20251226_225537.md
  pcap_analysis_VulnBook_20251226_193302.txt
  ai_pcap_analysis_20251226_223808.md
```

### New System (Sequential Numbers):

```
reports/
  log_analysis/
    report_1.csv
    report_1.json
    report_1.txt
    report_1.html
    ai_report_1.md
    report_2.csv
    report_2.json
    report_2.txt
    report_2.html
    ai_report_2.md
  pcap_analysis/
    report_1.txt
    ai_report_1.md
    report_2.txt
    ai_report_2.md
```

---

## 2. Directory Structure

### Two Main Categories:

1. **log_analysis/** - Windows Event Log reports and AI analysis
2. **pcap_analysis/** - Network traffic reports and AI analysis

### Removed:

- ❌ `ai_analysis/` folder (AI reports now go with their main reports)

---

## 3. Files Modified

### New File Created:

- **modules/report_numbering.py**
  - `get_next_report_number()` - Get sequential number for category
  - `get_report_filename()` - Generate filename with number
  - `load_counters()` / `save_counters()` - Track report numbers
  - Uses `.report_counter.json` to persist numbers

### Updated Files:

#### **modules/utils.py**

- `save_json_report()` - Now takes `report_number` parameter
- `save_csv_report()` - Now takes `report_number` parameter
- `save_text_summary()` - Now takes `report_number` parameter
- `save_html_report()` - Now takes `report_number` parameter
- All save to `log_analysis/` subdirectory with sequential naming

#### **modules/ai_analyzer.py**

- `analyze_report_with_ai()` - Added `report_number` parameter
  - Saves to `log_analysis/ai_report_{number}.md`
  - AI reports match their main report numbers
- `analyze_pcap_with_ai()` - Added `report_number` parameter
  - Saves to `pcap_analysis/ai_report_{number}.md`

#### **modules/pcap_analyzer.py**

- `generate_report()` - Returns `(report_file, report_number)`
  - Saves to `pcap_analysis/report_{number}.txt`
  - Uses sequential numbering via `report_numbering` module

#### **main.py**

- `run_automatic_analysis()` - Gets report number, passes to all save functions
- `run_file_analysis()` - Gets report number, passes to all save functions
- `run_pcap_tools()` - Receives report number from analyzer, passes to AI

#### **modules/report_manager.py**

- Removed `ai_analysis` category throughout
- Updated to show 2 categories instead of 3:
  - "📋 Log Analysis Reports (including AI)"
  - "📡 PCAP Analysis Reports (including AI)"
- Updated deletion menus and category mapping

---

## 4. Report Numbering System

### How It Works:

1. Counter stored in `reports/.report_counter.json`
2. Separate counters for `log_analysis` and `pcap_analysis`
3. Counter increments with each new analysis
4. All formats for same analysis get same number

### Example Counter File:

```json
{
  "log_analysis": 5,
  "pcap_analysis": 3
}
```

### Result:

- Next log analysis: `report_6.*` + `ai_report_6.md`
- Next PCAP analysis: `report_4.txt` + `ai_report_4.md`

---

## 5. Benefits

✅ **Easy Identification** - Simple numbered reports instead of long timestamps
✅ **Organized Structure** - Reports grouped by type in subdirectories  
✅ **AI Reports Together** - AI analysis saved next to main report with matching number
✅ **Sequential Tracking** - Easy to see how many analyses have been run
✅ **Clean Reports Folder** - No more files scattered at root level
✅ **Better Management** - Report manager shows categories clearly

---

## 6. Usage Examples

### Log Analysis Workflow:

```bash
# Run automatic scan
→ Generates: log_analysis/report_1.{csv,json,txt,html}

# Choose AI analysis (y)
→ Generates: log_analysis/ai_report_1.md

# Next scan
→ Generates: log_analysis/report_2.* + ai_report_2.md
```

### PCAP Analysis Workflow:

```bash
# Analyze PCAP file
→ Generates: pcap_analysis/report_1.txt

# Choose AI analysis (y)
→ Generates: pcap_analysis/ai_report_1.md

# Next PCAP
→ Generates: pcap_analysis/report_2.txt + ai_report_2.md
```

---

## 7. Report Management Menu

Updated menu structure:

```
Report Management
  1. View all reports by category
  2. Delete specific report by filename
  3. Delete all reports in a category
     - Log Analysis Reports (including AI)
     - PCAP Analysis Reports (including AI)
  4. Delete reports older than X days
  5. Delete all reports
  6. Back to main menu
```

---

## 8. Migration Notes

### Existing Reports:

- Old timestamp-based reports remain at root level
- Report manager can still view/delete them
- New reports use sequential numbering in subdirectories

### Clean Start (Optional):

To start fresh with sequential numbering:

1. Delete all files in `reports/` (except subdirectories)
2. Delete `.report_counter.json` to reset numbering
3. Run new analysis - will start at report_1

---

## 9. Technical Details

### Counter Persistence:

- Stored in `.report_counter.json` (hidden file)
- Survives program restarts
- JSON format for easy editing if needed

### Thread Safety:

- Current implementation: single-user, sequential
- Not concurrent-safe (fine for typical usage)

### Filename Validation:

- No spaces or special characters
- Simple numeric format: `report_N` and `ai_report_N`
- Works across all platforms (Windows, Linux, Mac)

---

## 10. Summary

The reporting system now provides:

- **Sequential numbering** (report_1, report_2, etc.)
- **Organized subdirectories** (log_analysis, pcap_analysis)
- **Paired AI reports** (ai_report_N matches report_N)
- **Simplified management** (2 categories instead of 3)
- **Clean structure** (no root-level clutter)

All new reports will automatically use this system. The changes are backwards compatible with the report management system which can still view and delete old timestamp-based reports.
