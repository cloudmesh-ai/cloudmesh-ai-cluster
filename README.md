# Local AI Slurm Cluster Documentation

This project provides a comprehensive, containerized environment for deploying and managing a multi-node Slurm cluster on a single host using Docker. It is designed for testing High-Performance Computing (HPC) configurations, AI job scheduling, and automation scripts without requiring dedicated physical hardware.

## Table of Contents
- Architecture
- Installation and Setup
- Cluster Management Tool (cmc)
- Operational Guide
- Configuration Details
- Directory Structure
- Troubleshooting

---

## Architecture

The cluster utilizes a distributed architecture simulated through Docker containers to mimic a physical HPC environment.

### Components
- **Controller Node (slurmctld)**: Central manager for resource allocation, job queuing, and node monitoring.
- **Compute Nodes (slurmd)**: Scalable worker containers that execute computational tasks.
- **Munge**: Lightweight authentication service for verifying identity across the cluster.
- **Docker Networking**: Dedicated bridge network for communication between controller and nodes.
- **Persistence**: State is managed via Docker volumes to ensure job history persists across restarts.

### Base Environment
- **Operating System**: Ubuntu 24.04
- **Scheduler**: Slurm Workload Manager
- **Containerization**: Docker and Docker Compose

---

## Installation and Setup

### Prerequisites
- Docker Engine (Latest Stable)
- Docker Compose V2
- Python 3.10+

### Initializing the Project
The "cmc cluster init" command prepares your environment using a hierarchical configuration pattern:

1. **Global Configuration**: Checks for a global directory at "~/.config/cloudmesh/cluster/".
2. **Template Seeding**: If the global directory is missing, it is created and seeded with default templates.
3. **Project Initialization**: Files are copied from the global directory into your current project directory.

To initialize a new cluster project:
"""bash
cmc cluster init
"""

### Launching the Cluster
Bring the cluster online:
"""bash
cmc cluster up
"""

### Verifying System Health
Ensure all compute nodes are active:
"""bash
cmc cluster status
"""

---

## Cluster Management Tool (cmc)

The "cmc" utility wraps Docker Compose to provide a simplified interface for cluster administration.

### Command Reference

| Command | Description | Usage Example |
| :--- | :--- | :--- |
| "init" | Initializes project files from global/template configs | "cmc cluster init" |
| "up" | Starts the controller and all compute nodes | "cmc cluster up" |
| "down" | Stops all cluster containers | "cmc cluster down" |
| "status" | Queries the Slurm controller for node status | "cmc cluster status" |
| "build" | Rebuilds the cluster Docker images | "cmc cluster build" |
| "install" | Performs a clean wipe, rebuild, and restart | "cmc cluster install" |
| "test" | Executes a smoke test job to verify cluster health | "cmc cluster test" |
| "shell" | Opens an interactive bash shell in the controller | "cmc cluster shell" |
| "reconfig" | Signals Slurm to reload its configuration | "cmc cluster reconfig" |
| "logs" | Streams logs from all cluster components | "cmc cluster logs" |
| "clean" | Wipes all volumes and resets cluster state | "cmc cluster clean" |
| "check-munge" | Verifies the Munge handshake between nodes | "cmc cluster check-munge" |

---

## Operational Guide

### Job Lifecycle
Use "cmc cluster shell" to enter the controller node.

1. **Submit a Job**:
   """bash
   sbatch my_ai_job.sh
   """

2. **Monitor Jobs**:
   """bash
   squeue
   """

3. **Cancel Jobs**:
   """bash
   scancel <job_id>
   """

### Scaling the Cluster
To change the number of compute nodes, modify the scale in "docker-compose.yml" or update "slurm.conf", then run "cmc cluster up".

---

## Configuration Details

### Slurm Configuration ("config/slurm.conf")
- **SlurmdParameters=config_overrides**: Forces Slurm to use config-defined resource limits rather than host hardware.
- **ProctrackType=proctrack/pgid**: Prevents conflicts with Docker Cgroup management.
- **Node Definitions**: Default support for "node[1-10]".

### Global Overrides
Maintain custom settings across projects in: "~/.config/cloudmesh/cluster/". These are used by "cmc cluster init".

---

## Directory Structure

"""text
.
├── Dockerfile          # Build definition
├── docker-compose.yml  # Service orchestration
├── Makefile            # Automation targets
├── README.md           # Documentation
├── setup_slurm.sh      # Slurm setup entrypoint
└── config/
    └── slurm.conf      # Slurm configuration
"""

---

## Troubleshooting

### Node State Issues
If nodes appear as "down" or "unk" in "sinfo":
1. "cmc cluster shell"
2. "scontrol update nodename=node[1-10] state=resume"

### Munge Authentication Failures
If you encounter credential errors:
1. "cmc cluster clean"
2. "cmc cluster up"
