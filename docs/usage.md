# Usage Guide

## Installation and Setup

### Prerequisites
- Docker Engine (Latest Stable)
- Docker Compose V2
- Python 3.10+

### Initializing the Project
The `cmc cluster init` command prepares your environment. It supports dynamic variable replacement and centralized configuration.

**Basic Initialization:**
```bash
cmc cluster init simple
```

**Advanced Initialization with Scaling and Variables:**
You can pass variables (e.g., node count `N`) directly to the command. These variables are used to generate the `slurm.conf` from a template (`slurm.conf.in`).
```bash
cmc cluster init simple N=3 A=hallo
```

### Launching the Cluster
Bring the cluster online:
```bash
cmc cluster start simple
```
*(If you omit the cluster name, it uses the current directory's configuration).*

### Verifying System Health
Ensure all compute nodes are active and the Slurm scheduler is responsive:
```bash
cmc cluster status simple
```

---

## Cluster Management Tool (cmc)

The `cmc cluster` tool wraps Docker Compose to provide a simplified interface for cluster administration. Most commands accept an optional `<cluster_name>` to target a specific cluster configuration.

### Command Reference

| Command | Description | Usage Example |
| :--- | :--- | :--- |
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
