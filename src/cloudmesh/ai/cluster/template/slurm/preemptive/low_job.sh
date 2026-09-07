#!/bin/bash
#SBATCH --job-name=test_low
#SBATCH --partition=low
#SBATCH --time=00:10:00
#SBATCH --output=low_%j.out

echo "Low priority job started at $(date)"
sleep 300
echo "Low priority job finished"