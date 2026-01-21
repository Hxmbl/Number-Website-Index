import os
import typer
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, SpinnerColumn
from concurrent.futures import ThreadPoolExecutor

app = typer.Typer()

def check_website(domain):
    """Internal check using netcat."""
    # Reduced ports to 443 and 80 for maximum speed
    for port in [443, 80]:
        if os.system(f"nc -zw1 {domain} {port} > /dev/null 2>&1") == 0:
            return True
    return False

@app.command()
def scan(limit: int = 1000):
    """Scans domains from 0.com up to the limit."""
    
    with Progress(
        SpinnerColumn(),
        # This TextColumn will now display the "description" which we update below
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        
        task = progress.add_task("Starting...", total=limit)
        
        def worker(i):
            domain = f"{i}.com"
            
            # Update the description to show the current domain being scanned
            progress.update(task, description=f"Checking: {domain}")
            
            if check_website(domain):
                progress.console.print(f"[bold green]FOUND:[/bold green] {domain}")
            
            progress.update(task, advance=1)

        # 50 threads is a good sweet spot for most 2026 home networks
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(worker, range(limit))
            
        # Set final message
        progress.update(task, description="[bold gold1]Scan Complete")

if __name__ == "__main__":
    app()
