#!/bin/bash

# Here is a comprehensive automated test script named `test.sh` that submits the jobs, 
# monitors their states in real-time, and outputs diagnostic information to prove 
# that preemption is functioning correctly.

echo "=========================================================="
echo "Starting Slurm Preemption Test Suite"
echo "=========================================================="

# Clean up any old output files
rm -f low_*.out high_*.out

echo ""
echo "[Step 1] Submitting long-running job to the LOW priority partition..."
LOW_JOB_ID=$(sbatch --parsable low_job.sh)
echo "-> Submitted low-priority job ID: $LOW_JOB_ID"

echo ""
echo "[Step 2] Waiting 3 seconds for the low job to initialize and occupy the node..."
sleep 3

echo ""
echo "[Step 3] Current cluster queue status (squeue):"
squeue

echo ""
echo "[Step 4] Submitting high-priority job to trigger preemption..."
HIGH_JOB_ID=$(sbatch --parsable high_job.sh)
echo "-> Submitted high-priority job ID: $HIGH_JOB_ID"

echo ""
echo "[Step 5] Monitoring queue immediately after high-priority submission..."
squeue

echo ""
echo "[Step 6] Waiting 5 seconds for high job execution and preemption action..."
sleep 5

echo ""
echo "[Step 7] Final cluster queue status (squeue):"
squeue

echo ""
echo "=========================================================="
echo "Verification Summary:"
echo "----------------------------------------------------------"
echo "Low-Priority Job ID:  $LOW_JOB_ID"
echo "High-Priority Job ID: $HIGH_JOB_ID"
echo ""
echo "Inspect the generated log files to confirm outcomes:"
echo "  - cat low_${LOW_JOB_ID}.out  (Should show termination/interruption)"
echo "  - cat high_${HIGH_JOB_ID}.out (Should show successful completion)"
echo "=========================================================="
