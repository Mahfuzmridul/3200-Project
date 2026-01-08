import win32evtlog  # type: ignore
import pandas as pd
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from config import MAX_EVENTS


def collect_windows_logs(log_type="Security", max_events=MAX_EVENTS):
    """
    Collect Windows event logs directly from system with progress indicator.

    Args:
        log_type: Type of Windows log to collect (Security, Application, System, etc.)
        max_events: Maximum number of events to collect

    Returns:
        DataFrame containing collected log events
    """
    server = "localhost"
    log_handle = None
    logs = []

    try:
        # Open event log
        log_handle = win32evtlog.OpenEventLog(server, log_type)

        # Get total number of records
        total = win32evtlog.GetNumberOfEventLogRecords(log_handle)

        print(f"\n[bold cyan]Collecting Windows '{log_type}' Logs...[/bold cyan]")
        print(f"[dim]Total available records: {total}[/dim]")
        print(f"[dim]Collecting up to: {max_events} events[/dim]")

        flags = (
            win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        )
        events = 0

        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:

            task = progress.add_task("[cyan]Reading events...", total=max_events)

            while events < max_events:
                try:
                    records = win32evtlog.ReadEventLog(log_handle, flags, 0)
                    if not records:
                        break

                    for record in records:
                        try:
                            events += 1

                            # Extract event data
                            logs.append(
                                {
                                    "TimeGenerated": record.TimeGenerated.Format(),
                                    "EventID": record.EventID & 0xFFFF,
                                    "SourceName": record.SourceName,
                                    "EventCategory": record.EventCategory,
                                    "EventType": record.EventType,
                                    "Computer": record.ComputerName,
                                    "Message": (
                                        str(record.StringInserts)
                                        if record.StringInserts
                                        else "No message"
                                    ),
                                    "RecordNumber": record.RecordNumber,
                                }
                            )

                            progress.update(task, advance=1)

                            if events >= max_events:
                                break

                        except Exception as record_error:
                            # Skip individual records that fail to parse
                            continue

                except Exception as read_error:
                    print(
                        f"[yellow]Warning: Error reading log batch: {str(read_error)}[/yellow]"
                    )
                    break

        print(f"[bold green]✓ Successfully collected {len(logs)} events[/bold green]")

        if not logs:
            print(
                "[yellow]⚠️ No logs were collected. This might be a permissions issue.[/yellow]"
            )
            return pd.DataFrame()

        return pd.DataFrame(logs)

    except Exception as e:
        print(f"[bold red]✗ Error collecting Windows logs: {str(e)}[/bold red]")

        # Provide helpful error messages
        if "Access is denied" in str(e) or "PermissionError" in str(e):
            print(
                "[yellow]💡 Tip: Run this program as Administrator to access system logs.[/yellow]"
            )
        elif "The system cannot find the file specified" in str(e):
            print(
                f"[yellow]💡 Tip: The log type '{log_type}' might not exist on this system.[/yellow]"
            )
            print("[yellow]Available log types: Security, Application, System[/yellow]")

        return pd.DataFrame()

    finally:
        # Always close the log handle
        if log_handle:
            try:
                win32evtlog.CloseEventLog(log_handle)
            except:
                pass


def get_available_log_types():
    """Get list of available Windows event log types."""
    try:
        import win32evtlog

        server = "localhost"

        common_logs = ["Security", "Application", "System", "Setup"]
        available = []

        for log_type in common_logs:
            try:
                handle = win32evtlog.OpenEventLog(server, log_type)
                win32evtlog.CloseEventLog(handle)
                available.append(log_type)
            except:
                pass

        return available
    except Exception as e:
        print(f"[yellow]Could not enumerate log types: {e}[/yellow]")
        return ["Security", "Application", "System"]
