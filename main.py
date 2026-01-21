import os
import typer
import csv
import threading
from datetime import datetime
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, SpinnerColumn
from concurrent.futures import ThreadPoolExecutor

app = typer.Typer()
# Create a lock so only one thread can write to the CSV at a time
csv_lock = threading.Lock()

def check_website(domain):
    """Internal check using netcat."""
    for port in [443, 80]:
        if os.system(f"nc -zw1 {domain} {port} > /dev/null 2>&1") == 0:
            return True, port
    return False, None

def save_to_csv(domain, port):
    """Appends found domain to CSV in a thread-safe way."""
    file_exists = os.path.isfile("found_domains.csv")
    
    with csv_lock:
        with open("found_domains.csv", mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write header only if the file is being created for the first time
            if not file_exists:
                writer.writerow(["Domain", "Port", "Status", "Discovery_Time"])
            
            writer.writerow([domain, port, "Online", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

@app.command()
def scan(limit: int = 1000):
    """Scans domains from 0.com up to the limit and saves to CSV."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        
        task = progress.add_task("Starting...", total=limit)
        
        def worker(i):
            domain = f"{i}.com"
            progress.update(task, description=f"Checking: {domain}")
            
            is_up, port = check_website(domain)
            if is_up:
                progress.console.print(f"[bold green]FOUND:[/bold green] {domain} (Port {port})")
                save_to_csv(domain, port)
            
            progress.update(task, advance=1)

        # 50 threads for high speed
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(worker, range(limit))
            
        progress.update(task, description="[bold gold1]Scan Complete")

if __name__ == "__main__":
    app()
