import os
import json
import csv
from datetime import datetime
from rich import print


def ensure_dir(path):
    """Ensure directory exists, create if it doesn't."""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"[green]✓ Created directory: {path}[/green]")
        return True
    except Exception as e:
        print(f"[bold red]✗ Error creating directory {path}: {e}[/bold red]")
        return False


def choose_log_file(user_log_dir):
    """Interactive log file selector with validation."""
    ensure_dir(user_log_dir)

    # Support multiple log formats
    supported_extensions = [".evtx", ".csv", ".json", ".log"]
    files = [
        f
        for f in os.listdir(user_log_dir)
        if any(f.lower().endswith(ext) for ext in supported_extensions)
    ]

    if not files:
        print(f"[yellow]⚠️ No log files found in {user_log_dir}.[/yellow]")
        print(f"[cyan]Supported formats: {', '.join(supported_extensions)}[/cyan]")
        print("[cyan]Please copy your log file there and rerun the program.[/cyan]")
        return None

    print("\n[bold underline cyan]Available Log Files:[/bold underline cyan]")
    for i, f in enumerate(files, start=1):
        file_path = os.path.join(user_log_dir, f)
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)
        print(f"  [green]{i}.[/green] {f} [dim]({size_mb:.2f} MB)[/dim]")

    while True:
        try:
            choice = input("\nEnter file number to analyze (or 'q' to quit): ").strip()

            if choice.lower() == "q":
                return None

            index = int(choice) - 1
            if 0 <= index < len(files):
                selected_file = os.path.join(user_log_dir, files[index])
                print(f"[bold green]✓ Selected: {files[index]}[/bold green]")
                return selected_file
            else:
                print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            print("[red]Invalid input. Please enter a number.[/red]")
        except KeyboardInterrupt:
            print("\n[yellow]Operation cancelled.[/yellow]")
            return None


def save_json_report(df, report_dir, report_number=None):
    """Save DataFrame as JSON report with error handling."""
    try:
        from modules.report_numbering import get_report_filename

        # Get sequential filename in log_analysis subdirectory
        if report_number:
            # Use existing report number
            subdir = os.path.join(report_dir, "log_analysis")
            ensure_dir(subdir)
            output_path = os.path.join(subdir, f"report_{report_number}.json")
        else:
            output_path, _ = get_report_filename(
                report_dir, "log_analysis", ".json", is_ai=False
            )

        # Convert DataFrame to JSON
        df.to_json(output_path, orient="records", indent=2, date_format="iso")

        file_size = os.path.getsize(output_path)
        size_kb = file_size / 1024
        print(f"[cyan]✓ JSON report saved: {output_path} ({size_kb:.2f} KB)[/cyan]")
        return output_path
    except Exception as e:
        print(f"[bold red]✗ Error saving JSON report: {e}[/bold red]")
        return None


def save_csv_report(df, report_dir, report_number=None):
    """Save DataFrame as CSV report."""
    try:
        from modules.report_numbering import get_report_filename

        # Get sequential filename in log_analysis subdirectory
        if report_number:
            # Use existing report number
            subdir = os.path.join(report_dir, "log_analysis")
            ensure_dir(subdir)
            output_path = os.path.join(subdir, f"report_{report_number}.csv")
        else:
            output_path, _ = get_report_filename(
                report_dir, "log_analysis", ".csv", is_ai=False
            )

        # Remove RawXML column if it exists (too large for CSV)
        if "RawXML" in df.columns:
            df_export = df.drop(columns=["RawXML"])
        else:
            df_export = df

        df_export.to_csv(output_path, index=False, encoding="utf-8")

        file_size = os.path.getsize(output_path)
        size_kb = file_size / 1024
        print(f"[cyan]✓ CSV report saved: {output_path} ({size_kb:.2f} KB)[/cyan]")
        return output_path
    except Exception as e:
        print(f"[bold red]✗ Error saving CSV report: {e}[/bold red]")
        return None


def save_text_summary(findings, report_dir, report_number=None):
    """Save analysis findings as text summary."""
    try:
        from modules.report_numbering import get_report_filename

        # Get sequential filename in log_analysis subdirectory
        if report_number:
            # Use existing report number
            subdir = os.path.join(report_dir, "log_analysis")
            ensure_dir(subdir)
            output_path = os.path.join(subdir, f"report_{report_number}.txt")
        else:
            output_path, _ = get_report_filename(
                report_dir, "log_analysis", ".txt", is_ai=False
            )

        with open(output_path, "w", encoding="utf-8") as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("WINDOWS LOG ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Findings
            f.write("SECURITY FINDINGS:\n")
            f.write("-" * 80 + "\n")
            for line in findings:
                f.write(f"{line}\n")

            # Footer
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")

        print(f"[yellow]✓ Summary saved: {output_path}[/yellow]")
        return output_path
    except Exception as e:
        print(f"[bold red]✗ Error saving summary: {e}[/bold red]")
        return None


def save_html_report(df, findings, report_dir, report_number=None):
    """Generate an HTML report with styling."""
    try:
        from modules.report_numbering import get_report_filename

        # Get sequential filename in log_analysis subdirectory
        if report_number:
            # Use existing report number
            subdir = os.path.join(report_dir, "log_analysis")
            ensure_dir(subdir)
            output_path = os.path.join(subdir, f"report_{report_number}.html")
        else:
            output_path, _ = get_report_filename(
                report_dir, "log_analysis", ".html", is_ai=False
            )

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Windows Log Analysis Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
        }}
        .findings {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .critical {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .warning {{
            color: #f39c12;
            font-weight: bold;
        }}
        .success {{
            color: #27ae60;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: #34495e;
            color: white;
            padding: 10px;
            text-align: left;
        }}
        td {{
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Windows Log Analysis Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="findings">
        <h2>Security Findings</h2>
        <ul>
"""

        for finding in findings:
            css_class = ""
            if "CRITICAL" in finding or "🔴" in finding:
                css_class = "critical"
            elif "WARNING" in finding or "⚠️" in finding:
                css_class = "warning"
            elif "✅" in finding:
                css_class = "success"

            html_content += f'            <li class="{css_class}">{finding}</li>\n'

        html_content += """
        </ul>
    </div>
    
    <div class="findings">
        <h2>Event Data Summary</h2>
"""

        # Add table with first 100 rows
        if not df.empty:
            df_display = df.head(100)
            # Remove RawXML for HTML display
            if "RawXML" in df_display.columns:
                df_display = df_display.drop(columns=["RawXML"])

            html_content += df_display.to_html(index=False, classes="data-table")

        html_content += """
    </div>
</body>
</html>
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[magenta]✓ HTML report saved: {output_path}[/magenta]")
        return output_path
    except Exception as e:
        print(f"[bold red]✗ Error saving HTML report: {e}[/bold red]")
        return None
