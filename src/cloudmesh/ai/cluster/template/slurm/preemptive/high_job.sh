#!/bin/bash
#SBATCH --job-name=test_high
#SBATCH --partition=high
#SBATCH --time=00:05:00
#SBATCH --output=high_%j.out

echo "High priority job started at $(date)"
sleep 10
echo "High priority job finished"