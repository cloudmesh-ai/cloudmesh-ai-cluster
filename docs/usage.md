# Usage Guide

## Installation and Setup

### Prerequisites
- Docker Engine (Latest Stable)
- Docker Compose V2
- Python 3.10+

### Initializing the Project
The `cmc cluster init` command prepares your environment. It supports dynamic profile resolution and variable replacement.

**Exploring Profiles:**
Before initializing, you can list the available cluster configurations:

```bash
cmc cluster init list
```

**Basic Initialization:**
Initialize a cluster using the default `simple` profile:

```bash
cmc cluster init simple
```

**Profile-Based Initialization:**
Initialize a cluster using a specific profile (e.g., `preemptive`) by using its name as the cluster name.

```bash
cmc cluster init preemptive
```

**Advanced Initialization with Scaling and Variables:**
You can pass variables (e.g., node count `N`) directly to the command. These variables are used to generate the `slurm.conf` from a template.

```bash
cmc cluster init preemptive N=3
```

### Launching the Cluster

Bring the cluster online:

```bash
cmc cluster start
```

*(If you omit the cluster name, it uses the current directory's configuration).*

### Verifying System Health

Ensure all compute nodes are active and the Slurm scheduler is responsive:

```bash
cmc cluster status simple
```

---

## Cluster Profiles

The tool provides different profiles to simulate various HPC environments. Each profile consists of a set of Dockerfiles, Compose files, and Slurm configurations.

| Profile | Description | Key Features |
| :--- | :--- | :--- |
| `simple` | Standard Slurm setup | Basic scheduler, 1 controller, N nodes |
| `preemptive` | Preemption-capable setup | High/Low priority jobs, preemption logic |

When a profile is selected, all accompanying scripts (e.g., `high_job.sh`, `low_job.sh` in the `preemptive` profile) are automatically copied to your cluster root.

---

## Cluster Management Tool (cmc)

The `cmc cluster` tool wraps Docker Compose to provide a simplified interface for cluster administration. Most commands accept an optional `<cluster_name>` to target a specific cluster configuration.

### Command Reference

| Command | Description | Usage Example |
| :--- | :--- | :--- |
| `init list` | Lists available cluster profiles | `cmc cluster init list` |
| `init` | Initializes project files with variable support | `cmc cluster init simple N=3` |
| `start` | Starts the controller and compute nodes | `cmc cluster start simple` |
| `stop` | Stops all cluster containers | `cmc cluster stop simple` |
| `status` | Queries Docker and Slurm (`sinfo`) for status | `cmc cluster status simple` |
| `build` | Rebuilds the cluster Docker images | `cmc cluster build simple` |
| `install` | Performs a clean wipe, rebuild, and restart | `cmc cluster install simple` |
| `test` | Runs a real `sbatch` smoke test job | `cmc cluster test simple` |
| `login` | Opens an interactive shell in the controller | `cmc cluster login simple` |
| `reconfig` | Signals Slurm to reload its configuration | `cmc cluster reconfig simple` |
| `logs` | Streams logs from all cluster components | `cmc cluster logs simple` |
| `clean` | Wipes all volumes and resets cluster state | `cmc cluster clean simple` |
| `check-munge` | Verifies the Munge handshake between nodes | `cmc cluster check-munge simple` |

---

## Operational Guide

### Container Environment
To facilitate easy development and testing, the cluster root directory on your host is mounted to `/home/slurm` inside the containers. The container's default working directory is also set to `/home/slurm`. 

This means that any script you add to the cluster root (e.g., `test_job.sh`) is immediately available inside the container.

### Job Lifecycle
Use `cmc cluster login` to enter the controller node.

1. **Submit a Job**:

   ```bash
   sbatch test_job.sh
   ```

2. **Monitor Jobs**:

   ```bash
   squeue
   ```

3. **Cancel Jobs**:

   ```bash
   scancel <job_id>
   ```

### Scaling the Cluster

Scaling is now handled during initialization. Pass the `N` variable to specify the number of worker nodes:

```bash
cmc cluster init simple N=5
cmc cluster start simple
```

The tool automatically configures `SLURM_NODES` in the `.env` file and applies `--scale node=N` during startup.

---

## Troubleshooting

### Node State Issues
If nodes appear as `down` or `unk` in `sinfo`:
1. `cmc cluster login <name>`
2. `scontrol update nodename=node[1-10] state=resume`

### Munge Authentication Failures
If you encounter credential errors:
1. `cmc cluster clean <name>`
2. `cmc cluster start <name>`
