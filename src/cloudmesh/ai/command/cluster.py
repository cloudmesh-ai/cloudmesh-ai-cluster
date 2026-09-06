# Copyright 2026 Gregor von Laszewski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#

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
        console.print("Run [yellow]cmc cluster init[/yellow] first to set up the cluster files.")
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
@click.option("--config", "-c", default="simple", help="Configuration profile to use (e.g., simple, premtive).")
@click.option("--config-dir", "-d", default="config", help="Directory to place the configuration files.")
def init_cmd(config, config_dir):
    """Initialize the current directory with Slurm cluster template files."""
    template_dir = Path(__file__).parent.parent / "cluster" / "template"
    global_config_dir = Path.home() / ".config" / "cloudmesh" / "cluster"

    if not template_dir.exists():
        console.print(f"[bold red]Error: Template directory not found at {template_dir}[/bold red]")
        return

    # Ensure global config directory exists and is seeded with templates if necessary
    if not global_config_dir.exists():
        try:
            global_config_dir.mkdir(parents=True, exist_ok=True)
            for item in template_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, global_config_dir)
            console.print(f"[yellow]Initialized global config directory at {global_config_dir}[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Error creating global config directory: {e}[/bold red]")

    # Determine source directory for profile-specific files
    profile_dir = template_dir / "slurm" / config
    if not profile_dir.exists():
        console.print(f"[bold red]Error: Configuration profile '{config}' not found at {profile_dir}[/bold red]")
        return

    files_to_copy = [
        "Dockerfile",
        "Makefile",
        "docker-compose.yml",
        "slurm.conf",
        "README.md",
        "setup_slurm.sh"
    ]

    profile_specific_files = ["Dockerfile", "docker-compose.yml", "slurm.conf"]

    for filename in files_to_copy:
        # Determine if we use the profile directory or the base template directory
        if filename in profile_specific_files:
            src_file = profile_dir / filename
        else:
            src_file = template_dir / filename

        if src_file.exists():
            if filename == "slurm.conf":
                # Slurm configuration should be in the specified config directory
                dest_dir = Path(config_dir)
                dest_dir.mkdir(exist_ok=True)
                shutil.copy(src_file, dest_dir / filename)
            else:
                shutil.copy(src_file, Path("."))
            console.print(f"[green]Copied {filename} (profile: {config})[/green]")
        else:
            console.print(f"[yellow]Warning: {filename} not found in source ({src_file})[/yellow]")

    console.print("[bold green]Cluster initialization complete![/bold green]")
    console.print(f"Used profile: [yellow]{config}[/yellow], Config dir: [yellow]{config_dir}[/yellow]")
    console.print("You can now run [yellow]cmc cluster install[/yellow] or [yellow]cmc cluster build[/yellow].")

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
