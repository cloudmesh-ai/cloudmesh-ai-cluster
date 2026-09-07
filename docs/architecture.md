# Architecture

The cluster utilizes a distributed architecture simulated through Docker containers to mimic a physical HPC environment.

## Components

- **Controller Node (slurmctld)**: Central manager for resource allocation, job queuing, and node monitoring.
- **Compute Nodes (slurmd)**: Scalable worker containers that execute computational tasks.
- **Munge**: Lightweight authentication service for verifying identity across the cluster.
- **Docker Networking**: Dedicated bridge network for communication between controller and nodes.
- **Persistence**: State is managed via Docker volumes to ensure job history persists across restarts.

## Base Environment

- **Operating System**: Ubuntu 24.04
- **Scheduler**: Slurm Workload Manager
- **Containerization**: Docker and Docker Compose

## Configuration Details

### Template-Based Configuration (`slurm.conf.in`)
The cluster uses a template system for `slurm.conf`. Variables passed during `init` (e.g., `N=3`) are replaced in the template using the `{{ VARIABLE }}` or `{{VARIABLE}}` syntax.

### Centralized Storage
Configurations are stored by default in: `~/.config/cloudmesh/clusters/<cluster_name>/`. This allows you to manage multiple cluster profiles on one machine and switch between them simply by passing the name to `cmc` commands.

## Directory Structure

```text
. (Cluster Root)
├── .env                # Project name and scaling (SLURM_NODES)
├── docker-compose.yml  # Service orchestration
├── Dockerfile          # Build definition
├── entrypoint.sh       # Setup script
├── test_job.sh         # Smoke test batch script
└── config/
    └── slurm.conf      # Generated Slurm configuration
```
