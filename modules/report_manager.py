"""
Report management utilities - view, delete, and organize reports
"""

import os
import shutil
from rich import print
from rich.table import Table
from rich.console import Console
from datetime import datetime

console = Console()


def organize_reports(report_dir):
    """Organize reports into subdirectories by type."""
    # Create subdirectories (AI reports go with their main reports)
    log_reports_dir = os.path.join(report_dir, "log_analysis")
    pcap_reports_dir = os.path.join(report_dir, "pcap_analysis")

    os.makedirs(log_reports_dir, exist_ok=True)
    os.makedirs(pcap_reports_dir, exist_ok=True)

    return log_reports_dir, pcap_reports_dir


def get_report_category(filename):
    """Determine report category based on filename."""
    filename_lower = filename.lower()

    if "pcap" in filename_lower or "ai_report" in filename_lower:
        # AI reports for PCAP go in pcap_analysis
        return "pcap_analysis"
    else:
        # Log analysis and AI log reports go in log_analysis
        return "log_analysis"


def list_reports_by_category(report_dir):
    """List all reports organized by category."""
    if not os.path.exists(report_dir):
        print("[yellow]Reports directory not found[/yellow]")
        return {}

    reports = {"log_analysis": [], "pcap_analysis": []}

    # Check main directory
    for filename in os.listdir(report_dir):
        filepath = os.path.join(report_dir, filename)
        if os.path.isfile(filepath):
            category = get_report_category(filename)
            file_size = os.path.getsize(filepath) / 1024  # KB
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            reports[category].append(
                {
                    "name": filename,
                    "path": filepath,
                    "size": file_size,
                    "modified": file_time,
                }
            )

    # Check subdirectories
    for category in ["log_analysis", "pcap_analysis"]:
        subdir = os.path.join(report_dir, category)
        if os.path.exists(subdir):
            for filename in os.listdir(subdir):
                filepath = os.path.join(subdir, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath) / 1024
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    reports[category].append(
                        {
                            "name": filename,
                            "path": filepath,
                            "size": file_size,
                            "modified": file_time,
                        }
                    )

    # Sort by modified time (newest first)
    for category in reports:
        reports[category].sort(key=lambda x: x["modified"], reverse=True)

    return reports


def display_reports(report_dir):
    """Display reports in a formatted table."""
    reports = list_reports_by_category(report_dir)

    total_files = sum(len(reports[cat]) for cat in reports)

    if total_files == 0:
        print(f"[yellow]No reports found in '{report_dir}'[/yellow]")
        return reports

    print(f"\n[bold cyan]═══ Reports Summary ═══[/bold cyan]")
    print(f"Total Reports: {total_files}\n")

    # Display each category
    for category, display_name in [
        ("log_analysis", "📋 Log Analysis Reports (including AI)"),
        ("pcap_analysis", "📡 PCAP Analysis Reports (including AI)"),
    ]:
        if reports[category]:
            print(
                f"\n[bold yellow]{display_name}[/bold yellow] ({len(reports[category])} files)"
            )

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("#", style="dim", width=4)
            table.add_column("Filename", style="green")
            table.add_column("Size", justify="right", style="cyan")
            table.add_column("Modified", style="yellow")

            for idx, report in enumerate(reports[category], 1):
                table.add_row(
                    str(idx),
                    report["name"],
                    f"{report['size']:.2f} KB",
                    report["modified"].strftime("%Y-%m-%d %H:%M"),
                )

            console.print(table)

    return reports


def delete_report(report_path):
    """Delete a specific report file."""
    try:
        os.remove(report_path)
        return True, None
    except Exception as e:
        return False, str(e)


def delete_reports_by_category(report_dir, category):
    """Delete all reports in a specific category."""
    reports = list_reports_by_category(report_dir)

    if not reports[category]:
        return 0, "No reports in this category"

    count = 0
    errors = []

    for report in reports[category]:
        success, error = delete_report(report["path"])
        if success:
            count += 1
        else:
            errors.append(f"{report['name']}: {error}")

    if errors:
        return count, "; ".join(errors)
    return count, None


def delete_all_reports(report_dir):
    """Delete all reports."""
    reports = list_reports_by_category(report_dir)

    total = sum(len(reports[cat]) for cat in reports)
    if total == 0:
        return 0, "No reports to delete"

    count = 0
    errors = []

    for category in reports:
        for report in reports[category]:
            success, error = delete_report(report["path"])
            if success:
                count += 1
            else:
                errors.append(f"{report['name']}: {error}")

    if errors:
        return count, "; ".join(errors)
    return count, None


def delete_old_reports(report_dir, days=30):
    """Delete reports older than specified days."""
    from datetime import timedelta

    reports = list_reports_by_category(report_dir)
    cutoff_date = datetime.now() - timedelta(days=days)

    count = 0
    errors = []

    for category in reports:
        for report in reports[category]:
            if report["modified"] < cutoff_date:
                success, error = delete_report(report["path"])
                if success:
                    count += 1
                else:
                    errors.append(f"{report['name']}: {error}")

    if errors:
        return count, "; ".join(errors)
    return count, None


def manage_reports_menu(report_dir):
    """Interactive report management menu."""
    while True:
        try:
            print("\n[bold magenta]════ Report Management ════[/bold magenta]")
            print("  [cyan]1.[/cyan] View All Reports")
            print("  [cyan]2.[/cyan] Delete Specific Report")
            print("  [cyan]3.[/cyan] Delete by Category")
            print("  [cyan]4.[/cyan] Delete Old Reports (>30 days)")
            print("  [cyan]5.[/cyan] Delete All Reports")
            print("  [cyan]6.[/cyan] Back to Main Menu")

            choice = input("\n[?] Enter your choice (1-6): ").strip()

            if choice == "1":
                display_reports(report_dir)
                input("\nPress Enter to continue...")

            elif choice == "2":
                reports = display_reports(report_dir)
                total = sum(len(reports[cat]) for cat in reports)

                if total == 0:
                    input("\nPress Enter to continue...")
                    continue

                # Create a flat list of all reports
                all_reports = []
                for category in ["log_analysis", "ai_analysis", "pcap_analysis"]:
                    all_reports.extend(reports[category])

                try:
                    report_num = int(
                        input("\nEnter report number to delete (0 to cancel): ").strip()
                    )
                    if report_num == 0:
                        continue
                    if 1 <= report_num <= len(all_reports):
                        report = all_reports[report_num - 1]
                        confirm = (
                            input(f"Delete '{report['name']}'? (y/n): ").strip().lower()
                        )
                        if confirm == "y":
                            success, error = delete_report(report["path"])
                            if success:
                                print(f"[green]✓ Deleted: {report['name']}[/green]")
                            else:
                                print(f"[red]✗ Error: {error}[/red]")
                    else:
                        print("[red]Invalid report number[/red]")
                except ValueError:
                    print("[red]Invalid input[/red]")

                input("\nPress Enter to continue...")

            elif choice == "3":
                print("\n[bold]Select Category:[/bold]")
                print("  [cyan]1.[/cyan] Log Analysis Reports (including AI)")
                print("  [cyan]2.[/cyan] PCAP Analysis Reports (including AI)")

                cat_choice = input("\nEnter choice (1-2): ").strip()
                category_map = {
                    "1": "log_analysis",
                    "2": "pcap_analysis",
                }

                if cat_choice in category_map:
                    category = category_map[cat_choice]
                    confirm = (
                        input(f"Delete all reports in this category? (y/n): ")
                        .strip()
                        .lower()
                    )
                    if confirm == "y":
                        count, error = delete_reports_by_category(report_dir, category)
                        if error:
                            print(
                                f"[yellow]⚠ Deleted {count} reports with errors: {error}[/yellow]"
                            )
                        else:
                            print(f"[green]✓ Deleted {count} reports[/green]")
                else:
                    print("[red]Invalid choice[/red]")

                input("\nPress Enter to continue...")

            elif choice == "4":
                try:
                    days = int(
                        input(
                            "Delete reports older than how many days? (default 30): "
                        ).strip()
                        or "30"
                    )
                    confirm = (
                        input(f"Delete reports older than {days} days? (y/n): ")
                        .strip()
                        .lower()
                    )
                    if confirm == "y":
                        count, error = delete_old_reports(report_dir, days)
                        if error:
                            print(
                                f"[yellow]⚠ Deleted {count} reports with errors: {error}[/yellow]"
                            )
                        else:
                            print(f"[green]✓ Deleted {count} old reports[/green]")
                except ValueError:
                    print("[red]Invalid number[/red]")

                input("\nPress Enter to continue...")

            elif choice == "5":
                reports = list_reports_by_category(report_dir)
                total = sum(len(reports[cat]) for cat in reports)

                if total == 0:
                    print("[yellow]No reports to delete[/yellow]")
                else:
                    confirm = (
                        input(
                            f"[bold red]Delete ALL {total} reports? This cannot be undone! (yes/no): [/bold red]"
                        )
                        .strip()
                        .lower()
                    )
                    if confirm == "yes":
                        count, error = delete_all_reports(report_dir)
                        if error:
                            print(
                                f"[yellow]⚠ Deleted {count}/{total} reports with errors: {error}[/yellow]"
                            )
                        else:
                            print(f"[green]✓ Deleted all {count} reports[/green]")
                    else:
                        print("[yellow]Deletion cancelled[/yellow]")

                input("\nPress Enter to continue...")

            elif choice == "6":
                return
            else:
                print("[red]Invalid choice. Please try again.[/red]")

        except KeyboardInterrupt:
            print("\n[yellow]Returning to main menu...[/yellow]")
            return
        except Exception as e:
            print(f"[red]Error: {str(e)}[/red]")
            input("\nPress Enter to continue...")
