# PCAP File Upload and Management Module
import os
import shutil
from rich import print

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../upload")


def list_files():
    """List all PCAP files in the upload directory."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    files = [
        f
        for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".pcap") or f.endswith(".pcapng")
    ]
    if not files:
        print("[yellow]No .pcap or .pcapng files found.[/yellow]")
    else:
        print("\n[bold cyan]Uploaded PCAP Files:[/bold cyan]")
        for idx, f in enumerate(files, 1):
            file_path = os.path.join(UPLOAD_DIR, f)
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            print(f"  [green]{idx}.[/green] {f} [dim]({size_mb:.2f} MB)[/dim]")
    return files


def upload_file():
    """Upload a PCAP file to the upload directory."""
    src = input("Enter the path to the .pcap or .pcapng file to upload: ").strip()

    # Remove quotes if present
    src = src.strip('"').strip("'")

    if not os.path.isfile(src):
        print("[bold red]✗ File does not exist.[/bold red]")
        return
    if not (src.endswith(".pcap") or src.endswith(".pcapng")):
        print("[bold red]✗ Only .pcap or .pcapng files are allowed.[/bold red]")
        return
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    dest = os.path.join(UPLOAD_DIR, os.path.basename(src))
    if os.path.exists(dest):
        print("[yellow]A file with this name already exists.[/yellow]")
        overwrite = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != "y":
            print("[cyan]Upload cancelled.[/cyan]")
            return
    try:
        shutil.copy2(src, dest)
        file_size = os.path.getsize(dest)
        size_mb = file_size / (1024 * 1024)
        print(
            f"[bold green]✓ Uploaded {os.path.basename(src)} ({size_mb:.2f} MB)[/bold green]"
        )
    except Exception as e:
        print(f"[bold red]✗ Error uploading file: {e}[/bold red]")


def delete_file():
    """Delete a PCAP file from the upload directory."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    files = list_files()
    if not files:
        return
    try:
        idx = int(input("\nEnter the number of the file to delete: "))
        if 1 <= idx <= len(files):
            file_to_delete = files[idx - 1]
            file_path = os.path.join(UPLOAD_DIR, file_to_delete)
            confirm = (
                input(f"Are you sure you want to delete '{file_to_delete}'? (y/n): ")
                .strip()
                .lower()
            )
            if confirm == "y":
                os.remove(file_path)
                print(f"[bold green]✓ Deleted {file_to_delete}[/bold green]")
            else:
                print("[cyan]Deletion cancelled.[/cyan]")
        else:
            print("[bold red]✗ Invalid selection.[/bold red]")
    except ValueError:
        print("[bold red]✗ Invalid input. Please enter a number.[/bold red]")
    except Exception as e:
        print(f"[bold red]✗ Error deleting file: {e}[/bold red]")
