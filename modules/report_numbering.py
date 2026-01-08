"""
Report numbering utilities - manage sequential report numbers
"""

import os
import json
import re


def get_report_counter_file(report_dir):
    """Get path to the report counter file."""
    return os.path.join(report_dir, ".report_counter.json")


def load_counters(report_dir):
    """Load report counters from file."""
    counter_file = get_report_counter_file(report_dir)

    if os.path.exists(counter_file):
        try:
            with open(counter_file, "r") as f:
                return json.load(f)
        except:
            pass

    # Default counters
    return {"log_analysis": 0, "pcap_analysis": 0}


def save_counters(report_dir, counters):
    """Save report counters to file."""
    counter_file = get_report_counter_file(report_dir)
    try:
        with open(counter_file, "w") as f:
            json.dump(counters, f, indent=2)
    except Exception as e:
        print(f"[yellow]Warning: Could not save counters: {e}[/yellow]")


def get_next_report_number(report_dir, category):
    """
    Get next sequential report number for a category.

    Args:
        report_dir: Base report directory
        category: 'log_analysis' or 'pcap_analysis'

    Returns:
        int: Next report number
    """
    counters = load_counters(report_dir)
    counters[category] = counters.get(category, 0) + 1
    save_counters(report_dir, counters)
    return counters[category]


def get_report_filename(report_dir, category, file_extension, is_ai=False):
    """
    Generate sequential report filename.

    Args:
        report_dir: Base report directory
        category: 'log_analysis' or 'pcap_analysis'
        file_extension: File extension (e.g., '.txt', '.csv', '.json', '.html', '.md')
        is_ai: True if this is an AI analysis report

    Returns:
        tuple: (full_path, report_number)
    """
    # Get subdirectory
    subdir = os.path.join(report_dir, category)
    os.makedirs(subdir, exist_ok=True)

    # Get next number
    report_num = get_next_report_number(report_dir, category)

    # Generate filename
    if is_ai:
        filename = f"ai_report_{report_num}{file_extension}"
    else:
        filename = f"report_{report_num}{file_extension}"

    full_path = os.path.join(subdir, filename)

    return full_path, report_num
