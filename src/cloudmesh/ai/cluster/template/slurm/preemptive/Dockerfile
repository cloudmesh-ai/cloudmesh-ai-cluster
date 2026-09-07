FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y slurmd slurmctld munge sudo && rm -rf /var/lib/apt/lists/*

# Setup directories
RUN mkdir -p /var/spool/slurmctld /var/spool/slurmd /var/log/slurm /run/munge /etc/munge && \
    chown slurm:slurm /var/spool/slurmctld /var/spool/slurmd /var/log/slurm && \
    chown -R munge:munge /etc/munge /run/munge /var/lib/munge && \
    chmod 0711 /run/munge

# Create a unified munge key
RUN dd if=/dev/urandom bs=1 count=1024 > /etc/munge/munge.key && \
    chown munge:munge /etc/munge/munge.key && \
    chmod 400 /etc/munge/munge.key

# Setup entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
