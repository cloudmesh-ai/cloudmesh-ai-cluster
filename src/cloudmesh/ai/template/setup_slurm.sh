#!/bin/bash

# 1. Create slurm.conf
cat <<EOT > slurm.conf
ClusterName=docker_cluster
SlurmctldHost=slurmctld
MungeDir=/etc/munge
AuthType=auth/munge

NodeName=node[01-02] NodeAddr=node[01-02] CPUs=1 State=UNKNOWN
PartitionName=debug Nodes=node[01-02] Default=YES MaxTime=INFINITE State=UP

SlurmUser=slurm
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmdPidFile=/var/run/slurmd.pid
SlurmdSpoolDir=/var/spool/slurmd
StateSaveLocation=/var/spool/slurmctld
SlurmctldLogFile=/var/log/slurm/slurmctld.log
SlurmdLogFile=/var/log/slurm/slurmd.log
EOT

# 2. Create Dockerfile (Note the 'EOF' to prevent variable expansion)
cat <<'EOT' > Dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    slurmd slurmctld munge sudo \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/spool/slurmctld /var/spool/slurmd /var/log/slurm /run/munge \
    && chown slurm:slurm /var/spool/slurmctld /var/spool/slurmd /var/log/slurm \
    && chown munge:munge /run/munge

RUN dd if=/dev/urandom bs=1 count=1024 > /etc/munge/munge.key \
    && chown munge:munge /etc/munge/munge.key \
    && chmod 400 /etc/munge/munge.key

# Create the entrypoint script
cat <<INNER > /entrypoint.sh
#!/bin/bash
sudo -u munge /usr/sbin/munged --force

if [ "\$1" = "slurmctld" ]; then
    echo "Starting slurmctld..."
    exec /usr/sbin/slurmctld -D
elif [ "\$1" = "slurmd" ]; then
    echo "Starting slurmd..."
    exec /usr/sbin/slurmd -D
else
    exec "\$@"
fi
INNER

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
EOT

# 3. Create docker-compose.yml
cat <<EOT > docker-compose.yml
services:
  slurmctld:
    build: .
    container_name: slurmctld
    hostname: slurmctld
    command: slurmctld
    volumes:
      - ./slurm.conf:/etc/slurm/slurm.conf

  node01:
    build: .
    container_name: node01
    hostname: node01
    command: slurmd
    volumes:
      - ./slurm.conf:/etc/slurm/slurm.conf

  node02:
    build: .
    container_name: node02
    hostname: node02
    command: slurmd
    volumes:
      - ./slurm.conf:/etc/slurm/slurm.conf
EOT

echo "Files created. Now building..."
docker compose up -d --build
echo "Waiting 10s for cluster to stabilize..."
sleep 10
docker exec slurmctld scontrol update nodename=node[01-02] state=resume
echo "Done! Test with: docker exec slurmctld sinfo"
