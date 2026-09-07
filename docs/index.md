# Cloudmesh AI Slurm Cluster

This project provides a comprehensive, containerized environment for deploying and managing a multi-node Slurm cluster on a single host using Docker. It is designed for testing High-Performance Computing (HPC) configurations, AI job scheduling, and automation scripts without requiring dedicated physical hardware.

## Quick Start

Get your cluster up and running in minutes:

1. **Explore available profiles**:
   ```bash
   cmc cluster init list
   ```

2. **Initialize the cluster**:
   You can use a profile name as the cluster name to apply specific configurations (e.g., `preemptive`).
   ```bash
   cmc cluster init my-cluster N=3
   # OR use a specific profile:
   cmc cluster init preemptive N=3
   ```

3. **Start the containers**:
   ```bash
   cmc cluster start my-cluster
   ```

4. **Verify health**:
   ```bash
   cmc cluster status my-cluster
   ```

5. **Run a smoke test**:
   ```bash
   cmc cluster test my-cluster
   ```

For more detailed information, please see the [Architecture](architecture.md) and [Usage Guide](usage.md).
