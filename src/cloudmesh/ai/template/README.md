# SLURM-in-Docker Lab

A lightweight, multi-node Slurm cluster running in Docker. This environment is optimized for testing high-performance computing (HPC) configurations, job scheduling, and automation scripts without requiring dedicated hardware.

## Architecture

The cluster consists of three primary containers:

- **slurmctld**: The central controller daemon.

- **node01**: Compute node 01 (Configured for 1 CPU).

- **node02**: Compute node 02 (Configured for 1 CPU).

Authentication is handled via Munge, with a shared key and socket permissions synchronized across the cluster.

------------------------------------------------------------------------

## Quick Start

### 1. Fresh Installation

To perform a clean wipe of all state, rebuild the images, and start the cluster:

Bash

```         
make install
```

### 2. Standard Startup

If the images are already built and you wish to start the services:

Bash

```         
make up
```

### 3. Verify Health

Ensure the nodes are in the idle state (not unk\* or down):

Bash

```         
make status
```

------------------------------------------------------------------------

## Management Commands

|  |  |
|----|----|
| **Command** | **Description** |
| make status | Displays sinfo and detailed node states. |
| make test | Runs srun -N2 hostname to verify cluster connectivity. |
| make shell | Opens a bash shell inside the slurmctld container. |
| make clean | Stops the cluster and wipes all volumes (resets Slurm state). |
| make check-munge | Runs a diagnostic handshake test between the controller and nodes. |

------------------------------------------------------------------------

## Technical Details

### Hardware Overrides

Because this runs in Docker, Slurm is configured with SlurmdParameters=config_overrides. This allows the nodes to ignore the actual CPU count of the host machine and stick to the resource limits defined in slurm.conf.

### Process Tracking

This configuration uses ProctrackType=proctrack/pgid.

Standard Slurm deployments often use Linux Cgroups for process tracking. However, because Docker containers are themselves managed by Cgroups, nested management often leads to permission conflicts and container failure. The pgid (Process Group ID) tracking method is used here to ensure stability.

### Munge Authentication

To resolve "Permission Denied" errors on the Munge socket, the entrypoint script enforces the following during the boot sequence:

Bash

```         
chmod 777 /run/munge/munge.socket.2
```

This ensures the slurm user can successfully communicate with the munge daemon across different container users.

------------------------------------------------------------------------

## Project Structure

- **setup_slurm.sh**: The master script that generates slurm.conf, the Dockerfile, and docker-compose.yml.

- **Makefile**: The primary interface for cluster lifecycle management.

- **slurm.conf**: The configuration file mapped to /etc/slurm/slurm.conf in all containers.

## Troubleshooting

If sinfo returns "Zero Bytes transmitted," the controller process has likely encountered a corrupted state file or a permission error during startup.

Resolution: Run "make install" to wipe all volumes and perform a fresh initialization.

------------------------------------------------------------------------