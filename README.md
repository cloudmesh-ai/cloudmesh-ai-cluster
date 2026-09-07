# Cloudmesh AI Slurm Cluster

This project provides a comprehensive, containerized environment for deploying and managing a multi-node Slurm cluster on a single host using Docker. It is designed for testing High-Performance Computing (HPC) configurations, AI job scheduling, and automation scripts without requiring dedicated physical hardware.

## 🚀 Quick Start

Get your cluster up and running in minutes:

1. **Explore available profiles**:
   ```bash
   cmc cluster init list
   ```

2. **Initialize the cluster**:
   You can use a profile name (like `preemptive`) as the cluster name to apply specific configurations.
   ```bash
   cmc cluster init simple N=3
   # OR
   cmc cluster init preemptive N=3
   ```

3. **Start the containers**:
   ```bash
   cmc cluster start simple
   ```

4. **Verify health**:
   ```bash
   cmc cluster status simple
   ```

## 📚 Documentation

We use MkDocs for our full documentation. You can find detailed guides on:

- [Architecture & Configuration](docs/architecture.md) - Learn about dynamic profiles and container mounts.
- [Installation & Usage Guide](docs/usage.md) - Detailed command reference and operational guide.
- [API Reference](docs/api.md) - Technical API documentation.

## 🛠 Management Tool (cmc)

The `cmc cluster` tool provides a simplified interface for cluster administration.

| Command | Description |
| :--- | :--- |
| `init list` | List available cluster profiles |
| `init` | Initializes project files with variable support |
| `start` | Starts the controller and compute nodes |
| `stop` | Stops all cluster containers |
| `status` | Queries Docker and Slurm (`sinfo`) for status |
| `test` | Runs a real `sbatch` smoke test job |
| `login` | Opens an interactive shell in the controller |

For a full list of commands, see the [Usage Guide](docs/usage.md).
