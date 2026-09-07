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

### Dynamic Profile Resolution
The cluster supports multiple configuration profiles (e.g., `simple`, `preemptive`). When initializing a cluster, the tool resolves the profile using the following priority:
1. **Explicit**: If the `--config` or `-c` flag is used.
2. **Inferred**: If the cluster name matches a known profile directory in the templates.
3. **Default**: Falls back to the `simple` profile.

### Template-Based Configuration (`slurm.conf.in`)
Each profile contains a `slurm.conf.in` template. Variables passed during `init` (e.g., `N=3`) are replaced in the template using the `{{ VARIABLE }}` or `{{VARIABLE}}` syntax to generate the final `slurm.conf`.

### Centralized Storage
Configurations are stored by default in: `~/.config/cloudmesh/clusters/<cluster_name>/`. This allows you to manage multiple cluster profiles on one machine and switch between them simply by passing the name to `cmc` commands.

## Directory Structure

### Host Directory (Cluster Root)
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

### Container Environment
To provide seamless access to scripts and data, the entire cluster root directory is mounted inside the containers:
- **Mount Path**: `/home/slurm`
- **Working Directory**: The containers start in `/home/slurm`, meaning you can run your scripts directly (e.g., `./test_job.sh`) without navigating from the root `/`.
