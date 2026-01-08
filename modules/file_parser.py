from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view
import pandas as pd
import xml.etree.ElementTree as ET
from rich import print
from datetime import datetime


def parse_evtx_file(file_path):
    """Parse user-submitted Windows .evtx log file into a structured DataFrame."""
    entries = []

    try:
        print(f"[cyan]Parsing EVTX file: {file_path}[/cyan]")

        with Evtx(file_path) as log:
            for record in evtx_file_xml_view(log):
                try:
                    # Convert record to string properly
                    if isinstance(record, bytes):
                        raw_xml = record.decode("utf-8", errors="ignore")
                    elif isinstance(record, tuple):
                        raw_xml = (
                            record[0].decode("utf-8", errors="ignore")
                            if isinstance(record[0], bytes)
                            else str(record[0])
                        )
                    else:
                        raw_xml = str(record)

                    # Parse XML to extract structured data
                    root = ET.fromstring(
                        raw_xml if isinstance(raw_xml, (str, bytes)) else record
                    )

                    # Extract System information
                    system = root.find(
                        "{http://schemas.microsoft.com/win/2004/08/events/event}System"
                    )

                    entry = {
                        "RawXML": [raw_xml, {}]
                    }  # Store as tuple format for JSON compatibility

                    if system is not None:
                        # Event ID
                        event_id = system.find(
                            "{http://schemas.microsoft.com/win/2004/08/events/event}EventID"
                        )
                        entry["EventID"] = (
                            int(event_id.text) if event_id is not None else None
                        )

                        # Time Created
                        time_created = system.find(
                            "{http://schemas.microsoft.com/win/2004/08/events/event}TimeCreated"
                        )
                        if time_created is not None:
                            entry["TimeGenerated"] = time_created.get("SystemTime", "")
                        else:
                            entry["TimeGenerated"] = None

                        # Provider
                        provider = system.find(
                            "{http://schemas.microsoft.com/win/2004/08/events/event}Provider"
                        )
                        entry["SourceName"] = (
                            provider.get("Name", "") if provider is not None else ""
                        )

                        # Level (severity)
                        level = system.find(
                            "{http://schemas.microsoft.com/win/2004/08/events/event}Level"
                        )
                        entry["EventType"] = int(level.text) if level is not None else 0

                        # Computer
                        computer = system.find(
                            "{http://schemas.microsoft.com/win/2004/08/events/event}Computer"
                        )
                        entry["Computer"] = (
                            computer.text if computer is not None else ""
                        )

                        # Channel
                        channel = system.find(
                            "{http://schemas.microsoft.com/win/2004/08/events/event}Channel"
                        )
                        entry["EventCategory"] = (
                            channel.text if channel is not None else ""
                        )

                    # Extract EventData (for EventData format)
                    event_data = root.find(
                        "{http://schemas.microsoft.com/win/2004/08/events/event}EventData"
                    )
                    message_parts = []

                    if event_data is not None:
                        for data in event_data:
                            if data.text:
                                name = data.get("Name", "")
                                message_parts.append(f"{name}: {data.text}")

                    # Extract UserData (for UserData format events like 1102)
                    if not message_parts:
                        user_data = root.find(
                            "{http://schemas.microsoft.com/win/2004/08/events/event}UserData"
                        )
                        if user_data is not None:
                            # Extract all child elements
                            for child in user_data.iter():
                                if child.text and child.text.strip():
                                    tag = (
                                        child.tag.split("}")[-1]
                                        if "}" in child.tag
                                        else child.tag
                                    )
                                    message_parts.append(f"{tag}: {child.text.strip()}")

                    entry["Message"] = (
                        " | ".join(message_parts)
                        if message_parts
                        else "No message data"
                    )

                    entries.append(entry)

                except Exception as parse_error:
                    # If XML parsing fails, try to extract at least some basic info
                    if isinstance(record, bytes):
                        raw_xml = record.decode("utf-8", errors="ignore")
                    elif isinstance(record, tuple):
                        raw_xml = (
                            record[0].decode("utf-8", errors="ignore")
                            if isinstance(record[0], bytes)
                            else str(record[0])
                        )
                    else:
                        raw_xml = str(record)

                    # Try to extract EventID from XML string
                    event_id = None
                    computer = ""
                    time_gen = None

                    try:
                        import re

                        event_id_match = re.search(
                            r"<EventID[^>]*>(\d+)</EventID>", raw_xml
                        )
                        if event_id_match:
                            event_id = int(event_id_match.group(1))

                        computer_match = re.search(
                            r"<Computer>([^<]+)</Computer>", raw_xml
                        )
                        if computer_match:
                            computer = computer_match.group(1)

                        time_match = re.search(r'SystemTime="([^"]+)"', raw_xml)
                        if time_match:
                            time_gen = time_match.group(1)
                    except:
                        pass

                    entries.append(
                        {
                            "RawXML": [raw_xml, {}],
                            "EventID": event_id,
                            "TimeGenerated": time_gen,
                            "SourceName": "",
                            "EventType": 0,
                            "EventCategory": "",
                            "Computer": computer,
                            "Message": f"Partial parse - Error: {str(parse_error)}",
                        }
                    )

        print(
            f"[bold green]✓ Successfully parsed {len(entries)} records from {file_path}[/bold green]"
        )

        # Create DataFrame with proper column order
        df = pd.DataFrame(entries)

        # Reorder columns for better readability
        column_order = [
            "TimeGenerated",
            "EventID",
            "SourceName",
            "EventType",
            "EventCategory",
            "Computer",
            "Message",
            "RawXML",
        ]

        # Only include columns that exist
        available_columns = [col for col in column_order if col in df.columns]
        df = df[available_columns]

        return df

    except FileNotFoundError:
        print(f"[bold red]✗ File not found: {file_path}[/bold red]")
        return pd.DataFrame()
    except Exception as e:
        print(f"[bold red]✗ Error parsing EVTX file: {str(e)}[/bold red]")
        return pd.DataFrame()


def parse_csv_log(file_path):
    """Parse CSV log files."""
    try:
        df = pd.read_csv(file_path)
        print(
            f"[bold green]✓ Successfully loaded {len(df)} records from CSV[/bold green]"
        )
        return df
    except Exception as e:
        print(f"[bold red]✗ Error parsing CSV file: {str(e)}[/bold red]")
        return pd.DataFrame()


def parse_json_log(file_path):
    """Parse JSON log files."""
    try:
        df = pd.read_json(file_path)
        print(
            f"[bold green]✓ Successfully loaded {len(df)} records from JSON[/bold green]"
        )
        return df
    except Exception as e:
        print(f"[bold red]✗ Error parsing JSON file: {str(e)}[/bold red]")
        return pd.DataFrame()
