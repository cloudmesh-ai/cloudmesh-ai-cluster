#!/bin/bash

# Start the Munge daemon as the munge user
sudo -u munge /usr/sbin/munged --force

# Give Munge a second to create the socket, then fix permissions for communication
sleep 1
if [ -f /run/munge/munge.socket.2 ]; then
    chmod 777 /run/munge/munge.socket.2
fi

# Determine which Slurm service to start based on the command passed
if [ "$1" = "slurmctld" ]; then
    echo "Starting slurmctld (Controller)..."
    exec /usr/sbin/slurmctld -D -vvv
elif [ "$1" = "slurmd" ]; then
    echo "Starting slurmd (Compute Node)..."
    exec /usr/sbin/slurmd -D -vvv
else
    # If no specific service is requested, execute the provided command
    exec "$@"
fi
