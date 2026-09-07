# Copyright 2026 Gregor von Laszewski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#

import click
import subprocess
import shutil
import time
from pathlib import Path
from rich.console import Console

console = Console()

def run_command(cmd: list[str], cwd: Path = Path(".")):
    """Run a shell command and handle output/errors."""
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error executing {' '.join(cmd)}:[/bold red]")
        console.print(f"[red]{e.stderr or e.stdout}[/red]")
        return None
    except FileNotFoundError:
        console.print(f"[bold red]Error: Command '{cmd[0]}' not found. Please ensure it is installed.")
        return None

def run_docker_compose(action: str, extra_args: list[str] = [], cwd: Path = Path(".")):
    """Helper to run docker compose commands."""
    if not (cwd / "docker-compose.yml").exists():
        console.print(f"[bold red]Error: docker-compose.yml not found in {cwd}[/bold red]")
        console.print("Run [yellow]cmc cluster init[/yellow] first to set up the cluster files.")
        return None
    
    cmd = ["docker", "compose", action] + extra_args
    return run_command(cmd, cwd=cwd)

def build_cluster(cwd: Path = Path(".")):
    """Build the Docker images."""
    console.print("[bold blue]Building cluster images...[/bold blue]")
    return run_docker_compose("build", [], cwd=cwd)

def start_cluster(cwd: Path = Path(".")):
    """Start the cluster and stabilize."""
    console.print("[bold blue]Starting cluster containers...[/bold blue]")
    
    # Check for node count in .env file to support scaling
    extra_args = ["-d"]
    env_file = cwd / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("SLURM_NODES="):
                    nodes = line.split("=")[1].strip()
                    extra_args.extend(["--scale", f"node={nodes}"])
                    console.print(f"[yellow]Scaling to {nodes} worker nodes...[/yellow]")
    
    return run_docker_compose("up", extra_args, cwd=cwd)

def stop_cluster(cwd: Path = Path(".")):
    """Stop cluster and remove containers."""
    console.print("[bold blue]Stopping cluster...[/bold blue]")
    return run_docker_compose("down", [], cwd=cwd)

def clean_cluster(cwd: Path = Path(".")):
    """Stop cluster and WIPE all volumes/state (Clean slate)."""
    console.print("[bold red]Wiping cluster state and volumes...[/bold red]")
    return run_docker_compose("down", ["-v"], cwd=cwd)

def install_cluster(cwd: Path = Path(".")):
    """Full Clean Install: Wipe state, rebuild no-cache, and start."""
    console.print("[bold green]Performing full clean install...[/bold green]")
    clean_cluster(cwd=cwd)
    build_cluster(cwd=cwd)
    start_cluster(cwd=cwd)

def status_cluster(cwd: Path = Path(".")):
    """Check the current status of the Slurm cluster."""
    console.print("[bold blue]Checking Docker container status...[/bold blue]")
    docker_output = run_docker_compose("ps", [], cwd=cwd)
    if docker_output:
        console.print(docker_output)
    
    console.print("\n[bold blue]Checking Slurm node status (sinfo)...[/bold blue]")
    slurm_output = run_command(["docker", "compose", "exec", "-T", "slurmctld", "sinfo"], cwd=cwd)
    if slurm_output:
        console.print(f"[green]Slurm Node Status:[/green]\n{slurm_output}")
    else:
        console.print("[bold red]Error: Could not retrieve Slurm node status. Is the cluster started?[/bold red]")

def test_cluster(cwd: Path = Path(".")):
    """Run a smoke test job to verify Slurm scheduling and execution."""
    console.print("[bold blue]Running Slurm smoke test...[/bold blue]")
    
    # 1. Submit the test job
    submit_cmd = ["docker", "compose", "exec", "-T", "slurmctld", "sbatch", "test_job.sh"]
    submit_output = run_command(submit_cmd, cwd=cwd)
    
    if not submit_output:
        console.print("[bold red]Error: Failed to submit test job. Ensure test_job.sh exists.[/bold red]")
        return

    console.print(f"[green]Job submitted successfully:[/green] {submit_output.strip()}")
    
    # 2. Wait for the job to complete (simple polling)
    console.print("[yellow]Waiting for job to complete...[/yellow]")
    for _ in range(10):
        status = run_command(["docker", "compose", "exec", "-T", "slurmctld", "squeue", "-h"], cwd=cwd)
        if not status or "test_job" not in status:
            break
        time.sleep(2)
    
    # 3. Check for output file
    output_file = cwd / "test_job.out"
    if output_file.exists():
        content = output_file.read_text()
        console.print(f"\n[bold green]Job Output:[/bold green]\n{content}")
        console.print("[bold green]✓ Smoke test PASSED![/bold green]")
    else:
        console.print("[bold red]Error: test_job.out not found. Job may have failed.[/bold red]")

def check_munge_cluster(cwd: Path = Path(".")):
    """Verify Munge handshake between nodes."""
    console.print("[bold blue]Verifying Munge authentication...[/bold blue]")
    output = run_command(["docker", "compose", "exec", "-T", "slurmctld", "munge", "-n"], cwd=cwd)
    if output:
        console.print("[green]Munge is functioning correctly on the controller node.[/green]")

def login_cluster(cwd: Path = Path(".")):
    """Open an interactive bash shell in the controller."""
    console.print("[bold blue]Opening shell in slurmctld...[/bold blue]")
    try:
        subprocess.run(["docker", "compose", "exec", "slurmctld", "bash"], cwd=cwd)
    except Exception as e:
        console.print(f"[bold red]Error opening shell:[/bold red] {e}")

def reconfig_cluster(cwd: Path = Path(".")):
    """Signals Slurm to reload its configuration."""
    console.print("[bold blue]Reloading Slurm configuration...[/bold blue]")
    output = run_command(["docker", "compose", "exec", "-T", "slurmctld", "scontrol", "reconfigure"], cwd=cwd)
    if output:
        console.print("[green]Configuration reloaded successfully.[/green]")

def logs_cluster(cwd: Path = Path(".")):
    """Streams logs from all cluster components."""
    console.print("[bold blue]Streaming cluster logs (Ctrl+C to stop)...[/bold blue]")
    try:
        subprocess.run(["docker", "compose", "logs", "-f"], cwd=cwd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Logs stopped.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error streaming logs:[/bold red] {e}")

def print_working_dir(path: Path = Path.cwd()):
    """Print the working directory to provide context for the command."""
    console.print(f"Working Directory: {path}")
    if (path / "docker-compose.yml").exists():
        console.print("✓ Found docker-compose.yml in this directory.")
    else:
        console.print("❌ docker-compose.yml NOT found in this directory.")
    console.print("-" * 40)

@click.group(name="cluster")
def cluster_group():
    """Manage Slurm clusters."""
    pass

@cluster_group.command(name="init")
@click.argument("cluster_name", required=False)
@click.argument("vars", nargs=-1)
@click.option("--config", "-c", default=None, help="Cluster profile to use (e.g., simple, advanced).")
@click.option("--dir", "-d", default=".", help="Custom directory for cluster files. Defaults to current directory.")
def init_cmd(cluster_name, vars, config, dir):
    """Initialize a new Slurm cluster.
    
    Example: cmc cluster init simple N=3 A=hallo
    To list available templates: cmc cluster init list
    """
    
    # Define source directories relative to this file
    current_file_dir = Path(__file__).parent
    template_dir = (current_file_dir / "../cluster/template/slurm").resolve()
    
    # Handle 'list' command to show available templates
    if cluster_name == "list":
        if template_dir.exists() and template_dir.is_dir():
            profiles = [d.name for d in template_dir.iterdir() if d.is_dir()]
            if profiles:
                console.print("[bold blue]Available cluster profiles:[/bold blue]")
                for p in sorted(profiles):
                    console.print(f"- [green]{p}[/green]")
            else:
                console.print("[yellow]No profiles found in template directory.[/yellow]")
        else:
            console.print(f"[bold red]Error: Template directory not found at {template_dir}[/bold red]")
        return

    # Resolve target directory
    target_dir = Path(dir).expanduser().resolve()

    # Parse variables and resolve cluster name
    provided_vars = {}
    remaining_args = []
    
    potential_args = []
    if cluster_name:
        potential_args.append(cluster_name)
    potential_args.extend(vars)
    
    for arg in potential_args:
        if "=" in arg:
            k, v = arg.split("=", 1)
            provided_vars[k] = v
        else:
            remaining_args.append(arg)
            
    actual_name = remaining_args[0] if remaining_args else "default"

    # Dynamically resolve profile: 
    # 1. Use explicit --config if provided
    # 2. Use cluster_name if it matches a profile directory
    # 3. Fallback to 'simple'
    if config is None:
        if (template_dir / actual_name).is_dir():
            config = actual_name
        else:
            config = "simple"
    
    # Warning if directory is not empty
    if target_dir.exists() and any(target_dir.iterdir()):
        console.print(f"[bold yellow]Warning: Directory {target_dir} is not empty. Files may be overwritten.[/bold yellow]")

    target_dir.mkdir(parents=True, exist_ok=True)
    
    profile_dir = template_dir / config
    
    if not profile_dir.exists():
        console.print(f"[bold red]Error: Profile '{config}' not found in {template_dir}[/bold red]")
        return

    config_dir = "config"
    
    # Gather all files from template_dir and profile_dir
    all_template_files = [f for f in template_dir.iterdir() if f.is_file()]
    all_profile_files = [f for f in profile_dir.iterdir() if f.is_file()]
    
    # Use a dictionary to handle overrides: profile_dir overrides template_dir
    files_to_copy = {f.name: f for f in all_template_files}
    for f in all_profile_files:
        files_to_copy[f.name] = f
    
    # Filter out .in files (they are processed separately into config/) 
    # and slurm.conf (the generated output)
    filtered_files = {
        name: path for name, path in files_to_copy.items() 
        if not name.endswith(".in") and name != "slurm.conf"
    }

    for filename, src_file in filtered_files.items():
        dest_path = target_dir / filename
        shutil.copy(src_file, dest_path)
        console.print(f"[green]Copied {filename} -> {dest_path}[/green]")

    # Handle slurm.conf replacement from slurm.conf.in
    conf_in_path = profile_dir / "slurm.conf.in"
    if not conf_in_path.exists():
        conf_in_path = profile_dir / "slurm.conf" # Fallback

    if conf_in_path.exists():
        content = conf_in_path.read_text()
        for k, v in provided_vars.items():
            # Replace {{ k }} or {{k}}
            content = content.replace(f"{{{{ {k} }}}}", v).replace(f"{{{{{k}}}}}", v)
        
        dest_dir = target_dir / config_dir
        dest_dir.mkdir(exist_ok=True)
        dest_path = dest_dir / "slurm.conf"
        dest_path.write_text(content)
        console.print(f"[green]Generated {dest_path} from {conf_in_path.name} with variables: {provided_vars}[/green]")
    else:
        console.print("[bold red]Error: slurm.conf.in not found in profile directory![/bold red]")

    # Save node count and project name to .env
    nodes = provided_vars.get("N", provided_vars.get("SLURM_NODES", "1"))
    with open(target_dir / ".env", "w") as env_file:
        env_file.write(f"COMPOSE_PROJECT_NAME={actual_name}\n")
        env_file.write(f"SLURM_NODES={nodes}\n")
    console.print(f"[green]Set COMPOSE_PROJECT_NAME={actual_name} and SLURM_NODES={nodes} in {target_dir}/.env[/green]")

    console.print("\n[bold green]Cluster initialization complete![/bold green]")
    console.print(f"Cluster name: [yellow]{actual_name}[/yellow]")
    console.print(f"Location: [yellow]{target_dir}[/yellow]")
    console.print(f"Profile: [yellow]{config}[/yellow]")
    console.print("\nTo start using your cluster, run:")
    console.print(f"[bold cyan]cmc cluster start {actual_name}[/bold cyan]")

def resolve_cwd(cluster_name: str = None):
    """Resolve the working directory based on the cluster name."""
    if cluster_name:
        cwd = Path(f"~/.config/cloudmesh/clusters/{cluster_name}").expanduser().resolve()
        if not (cwd / "docker-compose.yml").exists():
            console.print(f"[bold red]Error: Cluster '{cluster_name}' not found at {cwd}[/bold red]")
            console.print(f"Please run [yellow]cmc cluster init {cluster_name}[/yellow] first.")
            return None
        return cwd
    return Path.cwd()

@cluster_group.command(name="build")
@click.argument("cluster_name", required=False)
def build_cmd(cluster_name):
    """Build the Docker images."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        build_cluster(cwd=cwd)

@cluster_group.command(name="start")
@click.argument("cluster_name", required=False)
def start_cmd(cluster_name):
    """Start the cluster and stabilize."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        start_cluster(cwd=cwd)

@cluster_group.command(name="stop")
@click.argument("cluster_name", required=False)
def stop_cmd(cluster_name):
    """Stop cluster and remove containers."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        stop_cluster(cwd=cwd)

@cluster_group.command(name="clean")
@click.argument("cluster_name", required=False)
def clean_cmd(cluster_name):
    """Stop cluster and WIPE all volumes/state (Clean slate)."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        clean_cluster(cwd=cwd)

@cluster_group.command(name="install")
@click.argument("cluster_name", required=False)
def install_cmd(cluster_name):
    """Full Clean Install: Wipe state, rebuild no-cache, and start."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        install_cluster(cwd=cwd)

@cluster_group.command(name="status")
@click.argument("cluster_name", required=False)
def status_cmd(cluster_name):
    """Check the current status of the Slurm cluster."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        status_cluster(cwd=cwd)

@cluster_group.command(name="test")
@click.argument("cluster_name", required=False)
def test_cmd(cluster_name):
    """Run a smoke test job across both nodes."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        test_cluster(cwd=cwd)

@cluster_group.command(name="check-munge")
@click.argument("cluster_name", required=False)
def check_munge_cmd(cluster_name):
    """Verify Munge handshake between nodes."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        check_munge_cluster(cwd=cwd)

@cluster_group.command(name="login")
@click.argument("cluster_name", required=False)
def login_cmd(cluster_name):
    """Open an interactive bash shell in the controller."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        login_cluster(cwd=cwd)

@cluster_group.command(name="reconfig")
@click.argument("cluster_name", required=False)
def reconfig_cmd(cluster_name):
    """Signals Slurm to reload its configuration."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        reconfig_cluster(cwd=cwd)

@cluster_group.command(name="logs")
@click.argument("cluster_name", required=False)
def logs_cmd(cluster_name):
    """Streams logs from all cluster components."""
    cwd = resolve_cwd(cluster_name)
    if cwd:
        print_working_dir(cwd)
        logs_cluster(cwd=cwd)

def register(cli):
    cli.add_command(cluster_group, name="cluster")
