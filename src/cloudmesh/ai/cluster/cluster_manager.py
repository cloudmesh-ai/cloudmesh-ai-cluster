#!/usr/bin/env python
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Optional


class ClusterManager:
    """
    Manages a local Slurm cluster running in Docker.
    
    This class provides methods to control the lifecycle of the cluster,
    including starting, stopping, scaling, and health checks.
    """

    def __init__(self, cluster_dir: str = '/Users/grey/work/cloudmesh-ai-cluster/cluster') -> None:
        """
        Initialize the ClusterManager with the path to the cluster configuration.

        Args:
            cluster_dir: Absolute path to the directory containing docker-compose.yml.
        """
        self.cluster_dir = cluster_dir
        self.compose_cmd = ['docker', 'compose', '-f', f'{self.cluster_dir}/docker-compose.yml']
        self.exec_ctl = ['docker', 'exec', 'slurmctld']

    def _run_command(self, cmd: list[str], capture_output: bool = False, shell: bool = False) -> subprocess.CompletedProcess:
        """
        Execute a system command.

        Args:
            cmd: The command to run as a list of strings.
            capture_output: Whether to capture stdout and stderr.
            shell: Whether to execute the command through the shell.

        Returns:
            The result of the subprocess execution.
        """
        try:
            return subprocess.run(
                cmd, 
                capture_output=capture_output, 
                text=True, 
                check=True, 
                shell=shell
            )
        except subprocess.CalledProcessError as e:
            error_payload = {
                'error': 'Command execution failed',
                'command': ' '.join(cmd),
                'exit_code': e.returncode,
                'stderr': e.stderr
            }
            print(json.dumps(error_payload, indent=2))
            sys.exit(e.returncode or 1)

    def up(self) -> None:
        """
        Bring up the cluster and resume nodes.
        """
        print("Bringing up the cluster...")
        self._run_command(self.compose_cmd + ['up', '-d'])
        
        print("Waking up nodes...")
        self._run_command(self.exec_ctl + ['scontrol', 'update', 'nodename=node[1-10]', 'state=resume'])
        
        self._run_command(self.compose_cmd + ['ps'])

    def down(self) -> None:
        """
        Stop the cluster containers.
        """
        print("Stopping the cluster...")
        self._run_command(self.compose_cmd + ['down'])

    def status(self) -> None:
        """
        Check the current status of the cluster using sinfo.
        """
        result = self._run_command(self.exec_ctl + ['sinfo'], capture_output=True)
        print(result.stdout)

    def shell(self) -> None:
        """
        Open an interactive bash shell in the slurmctld container.
        """
        subprocess.run(['docker', 'exec', '-it', 'slurmctld', 'bash'])

    def test(self) -> None:
        """
        Run a simple test job to verify cluster connectivity.
        """
        print("Running test job: srun -N1 hostname")
        result = self._run_command(self.exec_ctl + ['srun', '-N1', 'hostname'], capture_output=True)
        print(result.stdout)

    def speedtest(self) -> None:
        """
        Perform a performance test across available compute nodes.
        """
        print("Initiating cluster speedtest...")
        # Command to run on each node: generate 100MB of zeros and checksum them
        test_cmd = "bash -c 'echo \"Testing $(hostname)...\"; time dd if=/dev/zero bs=1M count=100 | sha256sum'"
        
        # Try to run on all nodes. srun will handle the allocation.
        # We use -N1 to run on one node as a baseline, or you can adjust based on cluster size.
        # For a real speedtest, we run it on all available nodes in the 'debug' partition.
        result = self._run_command(self.exec_ctl + ['srun', '-p', 'debug', '-n', '1', test_cmd], capture_output=True)
        print(result.stdout)

    def dir(self) -> None:
        """
        List the directory structure of the cluster management setup.
        """
        print(f"Cluster Directory Structure ({self.cluster_dir}):")
        for root, dirs, files in os.walk(self.cluster_dir):
            level = root.replace(self.cluster_dir, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                print(f"{sub_indent}{f}")

    def clean(self) -> None:
        """
        Stop the cluster and wipe all volumes and state.
        """
        print("Wiping all volumes and state...")
        self._run_command(self.compose_cmd + ['down', '-v'])

    def reconfig(self) -> None:
        """
        Reload the Slurm configuration without restarting the container.
        """
        print("Reloading Slurm configuration...")
        self._run_command(self.exec_ctl + ['scontrol', 'reconfig'])

    def scale(self, node_count: int) -> None:
        """
        Scale the number of compute nodes.

        Args:
            node_count: The target number of nodes.
        """
        print(f"Scaling nodes to {node_count}...")
        self._run_command(self.compose_cmd + ['up', '-d', '--scale', f'node={node_count}'])
        self._run_command(self.exec_ctl + ['scontrol', 'update', 'nodename=node[1-10]', 'state=resume'])

    def logs(self) -> None:
        """
        Follow the logs of the cluster.
        """
        self._run_command(self.compose_cmd + ['logs', '-f'])

