# Tutorial: Getting Started with Cloudmesh AI Slurm Cluster

This tutorial will guide you through deploying a containerized Slurm cluster on your local machine. We will look at two different scenarios: a standard "simple" cluster and a "preemptive" cluster designed for priority-based scheduling.

## Prerequisites

Before you begin, ensure you have the following installed:
- Docker Engine (Latest stable)
- Docker Compose V2
- Python 3.10+

---

## Scenario 1: The Standard Cluster (Simple)

The `simple` profile is ideal for basic HPC testing, script validation, and learning Slurm.

### 1. Initialize the Cluster
It is recommended to create a dedicated directory for each cluster instance:
```bash
mkdir simple
cd simple
cmc cluster init simple N=3
```
*This command creates the project files in the current directory, including a generated `slurm.conf` and the necessary Docker files.*

### 2. Launch and Verify
```bash
# Start the containers
cmc cluster start

# Check if all nodes are 'idle' and available
cmc cluster status
```

---

## Scenario 2: The Priority Cluster (Preemptive)

The `preemptive` profile is designed for more advanced scheduling tests. It includes configurations for high and low priority jobs, allowing higher-priority tasks to "preempt" (interrupt) lower-priority ones.

### 1. Initialize the Cluster
Create a dedicated directory for the preemptive setup:
```bash
mkdir preemptive
cd preemptive
cmc cluster init preemptive N=1
```
*Note: By using the name `preemptive`, the tool automatically applies the preemptive profile, including specialized scripts like `high_job.sh` and `low_job.sh`.*

### 2. Launch and Verify
```bash
# Start the containers
cmc cluster start

# Check status
cmc cluster status
```

---

## Basic Operations

Once your cluster is running, you can interact with it using these common commands:

### Entering the Cluster
To run `sbatch` or `squeue` commands, you need to enter the controller node:
```bash
cmc cluster login
```
*(Using `.` targets the cluster in the current directory).*

### Running a Job
Inside the controller, you can submit a job using the provided smoke test script:
```bash
sbatch test_job.sh
```

### Cleaning Up
To stop the cluster and wipe all state/volumes for a fresh start:
```bash
cmc cluster clean
```

## Summary Table

| Goal | Command |
| :--- | :--- |
| **List available profiles** | `cmc cluster init list` |
| **Basic 3-node setup** | `mkdir simple && cd simple && cmc cluster init simple N=3` |
| **Preemptive 1-node setup** | `mkdir preemptive && cd preemptive && cmc cluster init preemptive N=1` |
| **Check health** | `cmc cluster status .` |
| **Interactive Shell** | `cmc cluster login .` |
