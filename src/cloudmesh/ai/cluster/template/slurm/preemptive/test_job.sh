#!/bin/bash
#SBATCH --job-name=test_job
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=test_job.out

echo "Hello from Slurm node: $(hostname)"
echo "Current date and time: $(date)"
echo "Testing Slurm batch job execution..."
sleep 5
echo "Job completed successfully"
