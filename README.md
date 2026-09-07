# Cloudmesh AI Slurm Cluster

This project provides a comprehensive, containerized environment for deploying and managing a multi-node Slurm cluster on a single host using Docker. It is designed for testing High-Performance Computing (HPC) configurations, AI job scheduling, and automation scripts without requiring dedicated physical hardware.

## Documentation

Full documentation is available via MkDocs. Please refer to the following guides for detailed information:

- [Quick Start & Installation](docs/index.md) - Get your cluster up and running in minutes.
- [Architecture & Configuration](docs/architecture.md) - Learn about dynamic profiles and container mounts.
- [Usage Guide](docs/usage.md) - Detailed command reference and operational instructions.
- [API Reference](docs/api.md) - Technical API documentation.

## Fast Track

If you want to start immediately, the most common path is:

```bash
# 1. Initialize a simple cluster with 3 nodes
cmc cluster init simple N=3

# 2. Start the cluster
cmc cluster start simple

# 3. Check health
cmc cluster status simple
```

For a more detailed walkthrough, see the [TUTORIAL.md](./TUTORIAL.md) file.
