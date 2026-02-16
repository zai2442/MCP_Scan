import asyncio
import click
import logging
import json
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from uuid import UUID

from mcp_scan.core.scheduler import Scheduler
from mcp_scan.core.models import TaskStatus
from mcp_scan.config import get_config

console = Console()
scheduler = Scheduler()

logging.basicConfig(filename='mcp_scan.log', level=logging.INFO)

@click.group()
def cli():
    """MCP Scan - Distributed Penetration Testing Platform"""
    pass

@cli.command()
@click.option('--target', required=True, help='Target IP or URL')
@click.option('--profile', default='fast', help='Scan profile (fast/deep)')
def start(target, profile):
    """Start a new scan job."""
    console.print(f"[bold green]Starting scan on {target} with profile {profile}[/bold green]")
    
    async def run_scan():
        job = await scheduler.create_job(target)
        console.print(f"Job ID: [bold cyan]{job.id}[/bold cyan]")
        
        # Start the scheduler in background
        scan_task = asyncio.create_task(scheduler.run_job(job.id))
        
        # Live Display Loop
        with Live(generate_status_table(job.id), refresh_per_second=4) as live:
            while not scan_task.done():
                live.update(generate_status_table(job.id))
                await asyncio.sleep(0.5)
            
            # One final update
            live.update(generate_status_table(job.id))
        
        console.print("[bold green]Scan Completed![/bold green]")

    asyncio.run(run_scan())

@cli.command()
@click.argument('job_id')
def status(job_id):
    """Check status of a job."""
    try:
        uuid_id = UUID(job_id)
        table = generate_status_table(uuid_id)
        console.print(table)
    except ValueError:
        console.print("[red]Invalid Job ID format[/red]")

@cli.command()
@click.argument('job_id')
@click.option('--output', '-o', required=True, help='Output file path')
def report(job_id, output):
    """Export scan report."""
    try:
        uuid_id = UUID(job_id)
    except ValueError:
        console.print("[red]Invalid Job ID format[/red]")
        return

    job = scheduler.get_job(uuid_id)
    if job:
        data = job.model_dump()
    else:
        data = {"job_id": job_id, "error": "Job not found in current session"}

    try:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        console.print(f"[green]Report exported successfully: {output}[/green]")
    except OSError as e:
        console.print(f"[red]Failed to write report: {e}[/red]")

def generate_status_table(job_id: UUID) -> Table:
    job = scheduler.get_job(job_id)
    if not job:
        return Panel(f"[red]Job {job_id} not found[/red]")

    table = Table(title=f"Scan Status: {job.target} [{job.status.value}]")
    table.add_column("Task ID", style="dim", width=8)
    table.add_column("Tool", style="cyan")
    table.add_column("Status")
    table.add_column("Info")

    for task in job.tasks:
        status_color = "yellow"
        if task.status == TaskStatus.COMPLETED:
            status_color = "green"
        elif task.status == TaskStatus.FAILED:
            status_color = "red"
        elif task.status == TaskStatus.RUNNING:
            status_color = "blue"
        
        info = ""
        if task.error:
            info = f"[red]{task.error[:30]}...[/red]"
        elif task.result:
            info = "Done"

        table.add_row(
            str(task.id)[:8],
            task.tool_name,
            f"[{status_color}]{task.status.value}[/{status_color}]",
            info
        )
    return table

if __name__ == '__main__':
    cli()
