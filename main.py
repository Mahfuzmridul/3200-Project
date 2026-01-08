# Unified main entry point for merged_analyzer
from modules.log_collector import collect_windows_logs
from modules.file_parser import parse_evtx_file, parse_csv_log, parse_json_log
from modules.analyzer import detect_basic_anomalies
from modules.utils import (
    save_json_report,
    save_csv_report,
    save_text_summary,
    save_html_report,
    ensure_dir,
    choose_log_file,
)
from modules.ai_analyzer import analyze_report_with_ai
from modules.report_manager import manage_reports_menu, organize_reports
from modules.pcap_uploader import list_files, delete_file
from modules.pcap_analyzer import generate_report as auto_analyze_pcap
from config import (
    REPORT_DIR,
    USER_LOG_DIR,
    DEFAULT_LOG_TYPE,
    UPLOAD_DIR,
    AI_ANALYSIS_ENABLED,
)
from rich import print
from rich.console import Console
from rich.panel import Panel
import sys
import os

console = Console()


def print_banner():
    """Display application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        UNIFIED LOG & PCAP ANALYZER v2.0                     ║
    ║        Windows Event Log & Network Traffic Analysis          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold cyan"))


def run_automatic_analysis():
    """Run automatic Windows log analysis from live system."""
    try:
        print(
            "\n[bold cyan]════ Running Automatic Windows Log Analysis ════[/bold cyan]"
        )

        df = collect_windows_logs(DEFAULT_LOG_TYPE)

        if df is None or df.empty:
            print("[yellow]⚠️ No logs collected. Analysis skipped.[/yellow]")
            return

        findings = detect_basic_anomalies(df)

        # Save reports in multiple formats with sequential numbering
        print("\n[bold cyan]Generating reports...[/bold cyan]")

        # All reports for the same analysis get the same number
        from modules.report_numbering import get_next_report_number

        report_num = get_next_report_number(REPORT_DIR, "log_analysis")

        save_json_report(df, REPORT_DIR, report_number=report_num)
        save_csv_report(df, REPORT_DIR, report_number=report_num)
        save_text_summary(findings, REPORT_DIR, report_number=report_num)
        save_html_report(df, findings, REPORT_DIR, report_number=report_num)

        # Display findings
        print("\n[bold yellow]════ Analysis Findings ════[/bold yellow]")
        for finding in findings:
            print(f"  {finding}")

        print("\n[bold green]✓ Automatic analysis completed successfully![/bold green]")

        # Offer AI analysis
        if AI_ANALYSIS_ENABLED:
            ai_choice = (
                input(
                    "\n[?] Would you like AI-powered analysis and remediation guidance? (y/n): "
                )
                .strip()
                .lower()
            )
            if ai_choice == "y":
                analyze_report_with_ai(
                    df, findings, REPORT_DIR, report_number=report_num
                )

    except PermissionError:
        print(
            "[bold red]✗ Permission denied. Please run as Administrator to access system logs.[/bold red]"
        )
    except Exception as e:
        print(f"[bold red]✗ Error during automatic analysis: {str(e)}[/bold red]")

    input("\nPress Enter to continue...")


def run_file_analysis():
    """Run analysis on a user-provided log file."""
    try:
        print("\n[bold cyan]════ File-Based Log Analysis ════[/bold cyan]")

        file_path = choose_log_file(USER_LOG_DIR)
        if not file_path:
            return

        # Determine file type and parse accordingly
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".evtx":
            df = parse_evtx_file(file_path)
        elif file_ext == ".csv":
            df = parse_csv_log(file_path)
        elif file_ext == ".json":
            df = parse_json_log(file_path)
        else:
            print(f"[yellow]⚠️ Unsupported file format: {file_ext}[/yellow]")
            return

        if df is None or df.empty:
            print("[yellow]⚠️ No data parsed from file. Analysis skipped.[/yellow]")
            return

        findings = detect_basic_anomalies(df)

        # Generate unique filenames based on source file
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        print("\n[bold cyan]Generating reports...[/bold cyan]")

        # All reports for the same analysis get the same number
        from modules.report_numbering import get_next_report_number

        report_num = get_next_report_number(REPORT_DIR, "log_analysis")

        save_json_report(df, REPORT_DIR, report_number=report_num)
        save_csv_report(df, REPORT_DIR, report_number=report_num)
        save_text_summary(findings, REPORT_DIR, report_number=report_num)
        save_html_report(df, findings, REPORT_DIR, report_number=report_num)

        # Display findings
        print("\n[bold yellow]════ Analysis Findings ════[/bold yellow]")
        for finding in findings:
            print(f"  {finding}")

        print(
            f"\n[bold green]✓ Analysis of {os.path.basename(file_path)} completed successfully![/bold green]"
        )

        # Offer AI analysis
        if AI_ANALYSIS_ENABLED:
            ai_choice = (
                input(
                    "\n[?] Would you like AI-powered analysis and remediation guidance? (y/n): "
                )
                .strip()
                .lower()
            )
            if ai_choice == "y":
                analyze_report_with_ai(
                    df, findings, REPORT_DIR, report_number=report_num
                )

    except Exception as e:
        print(f"[bold red]✗ Error during file analysis: {str(e)}[/bold red]")

    input("\nPress Enter to continue...")


def run_pcap_tools():
    """PCAP tools submenu."""
    while True:
        try:
            print("\n[bold magenta]════ PCAP Analysis ════[/bold magenta]")
            print("  [cyan]1.[/cyan] List uploaded PCAP files")
            print("  [cyan]2.[/cyan] Automatic PCAP Analysis (Generate Report)")
            print("  [cyan]3.[/cyan] Delete a PCAP file")
            print("  [cyan]4.[/cyan] Back to main menu")

            choice = input("\n[?] Enter your choice (1-4): ").strip()

            if choice == "1":
                list_files()
                input("\nPress Enter to continue...")
            elif choice == "2":
                # Automatic PCAP Analysis
                files = list_files()
                if files:
                    try:
                        file_num = int(
                            input("\nEnter file number to analyze: ").strip()
                        )
                        if 1 <= file_num <= len(files):
                            pcap_path = os.path.join(UPLOAD_DIR, files[file_num - 1])
                            print(
                                f"\n[cyan]Starting automatic analysis of {files[file_num - 1]}...[/cyan]"
                            )
                            report_file, report_num = auto_analyze_pcap(
                                pcap_path, REPORT_DIR
                            )

                            # Offer AI analysis if enabled
                            if report_file and AI_ANALYSIS_ENABLED:
                                ai_choice = (
                                    input(
                                        "\n[?] Would you like AI-powered analysis and security insights? (y/n): "
                                    )
                                    .strip()
                                    .lower()
                                )
                                if ai_choice == "y":
                                    # Read the report content
                                    with open(report_file, "r", encoding="utf-8") as f:
                                        report_content = f.read()

                                    # Import AI analyzer function for PCAP
                                    from modules.ai_analyzer import analyze_pcap_with_ai

                                    analyze_pcap_with_ai(
                                        report_content,
                                        REPORT_DIR,
                                        report_number=report_num,
                                    )
                        else:
                            print("[red]Invalid file number.[/red]")
                    except ValueError:
                        print("[red]Invalid input. Please enter a number.[/red]")
                input("\nPress Enter to continue...")
            elif choice == "3":
                delete_file()
                input("\nPress Enter to continue...")
            elif choice == "4":
                return
            else:
                print("[red]Invalid choice. Please try again.[/red]")

        except KeyboardInterrupt:
            print("\n[yellow]Returning to main menu...[/yellow]")
            return
        except Exception as e:
            print(f"[bold red]Error in PCAP tools: {str(e)}[/bold red]")
            input("\nPress Enter to continue...")


def main_menu():
    """Main application menu."""
    try:
        # Ensure required directories exist
        ensure_dir(REPORT_DIR)
        ensure_dir(USER_LOG_DIR)
        ensure_dir(UPLOAD_DIR)

        while True:
            try:
                print_banner()
                print("\n[bold cyan]Main Menu:[/bold cyan]")
                print(
                    "  [green]1.[/green] Automatic Windows Log Analysis (Live System)"
                )
                print("  [green]2.[/green] Analyze a Log File from 'user_logs' Folder")
                print("  [green]3.[/green] PCAP Tools (Network Analysis)")
                print("  [green]4.[/green] Manage Reports (View/Delete/Organize)")
                print("  [green]5.[/green] Exit")

                choice = input("\n[?] Enter your choice (1-5): ").strip()

                if choice == "1":
                    run_automatic_analysis()
                elif choice == "2":
                    run_file_analysis()
                elif choice == "3":
                    run_pcap_tools()
                elif choice == "4":
                    # Organize reports into subdirectories first
                    organize_reports(REPORT_DIR)
                    # Show report management menu
                    manage_reports_menu(REPORT_DIR)
                elif choice == "5":
                    print(
                        "\n[bold yellow]Thank you for using Log & PCAP Analyzer![/bold yellow]"
                    )
                    print("[cyan]Stay secure! 🔒[/cyan]")
                    sys.exit(0)
                else:
                    print(
                        "[red]Invalid choice. Please enter a number between 1-5.[/red]"
                    )
                    input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n\n[yellow]Use option 5 to exit properly.[/yellow]")
                input("Press Enter to continue...")

    except Exception as e:
        print(f"[bold red]Fatal error: {str(e)}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[yellow]Program interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"\n[bold red]Unexpected error: {str(e)}[/bold red]")
        sys.exit(1)
