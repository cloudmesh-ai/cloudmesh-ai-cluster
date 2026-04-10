# Copyright 2026 Gregor von Laszewski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

import click
import subprocess
import shutil
from pathlib import Path
from rich.console import Console

console = Console()

def run_make(target: str):
    """Run a make target in the current directory."""
    if not Path("Makefile").exists():
        console.print("[bold red]Error: Makefile not found in current directory.[/bold red]")
        console.print("Run [yellow]cme cluster init[/yellow] first to set up the cluster files.")
        return

    try:
        subprocess.run(["make", target], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error running 'make {target}':[/bold red] {e}")
    except FileNotFoundError:
        console.print("[bold red]Error: 'make' command not found. Please install make.[/bold red]")

@click.group()
def cluster_group():
    """Cluster management extension for Slurm-in-Docker."""
    pass

@cluster_group.command(name="init")
def init_cmd():
    """Initialize the current directory with Slurm cluster template files."""
    template_dir = Path(__file__).parent / "template"
    if not template_dir.exists():
        console.print("[bold red]Error: Template directory not found.[/bold red]")
        return

    files_to_copy = [
        "Dockerfile",
        "Makefile",
        "docker-compose.yml",
        "slurm.conf",
        "README.md",
        "setup_slurm.sh"
    ]

    for filename in files_to_copy:
        src = template_dir / filename
        if src.exists():
            shutil.copy(src, Path("."))
            console.print(f"[green]Copied {filename}[/green]")
        else:
            console.print(f"[yellow]Warning: {filename} not found in template.[/yellow]")

    console.print("[bold green]Cluster initialization complete![/bold green]")
    console.print("You can now run [yellow]cme cluster install[/yellow] or [yellow]cme cluster build[/yellow].")

@cluster_group.command(name="build")
def build_cmd():
    """Build the Docker images."""
    run_make("build")

@cluster_group.command(name="up")
def up_cmd():
    """Start the cluster and stabilize."""
    run_make("up")

@cluster_group.command(name="down")
def down_cmd():
    """Stop cluster and remove containers."""
    run_make("down")

@cluster_group.command(name="clean")
def clean_cmd():
    """Stop cluster and WIPE all volumes/state (Clean slate)."""
    run_make("clean")

@cluster_group.command(name="install")
def install_cmd():
    """Full Clean Install: Wipe state, rebuild no-cache, and start."""
    run_make("install")

@cluster_group.command(name="status")
def status_cmd():
    """Check the current status of the Slurm cluster."""
    run_make("status")

@cluster_group.command(name="test")
def test_cmd():
    """Run a smoke test job across both nodes."""
    run_make("test")

@cluster_group.command(name="check-munge")
def check_munge_cmd():
    """Verify Munge handshake between nodes."""
    run_make("check-munge")

def register(cli):
    cli.add_command(cluster_group, name="cluster")
