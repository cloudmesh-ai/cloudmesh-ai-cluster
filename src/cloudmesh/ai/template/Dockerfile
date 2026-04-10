FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    slurmd slurmctld munge sudo \
    && rm -rf /var/lib/apt/lists/*

# Setup directories
RUN mkdir -p /var/spool/slurmctld /var/spool/slurmd /var/log/slurm /run/munge /etc/munge \
    && chown slurm:slurm /var/spool/slurmctld /var/spool/slurmd /var/log/slurm \
    && chown -R munge:munge /etc/munge /run/munge /var/lib/munge \
    && chmod 0711 /run/munge

# Create a unified munge key
RUN dd if=/dev/urandom bs=1 count=1024 > /etc/munge/munge.key \
    && chown munge:munge /etc/munge/munge.key \
    && chmod 400 /etc/munge/munge.key

# FIXED ENTRYPOINT: Added socket permission fix
RUN echo '#!/bin/bash\n\
sudo -u munge /usr/sbin/munged --force\n\
# Give Munge a second to create the socket, then fix permissions\n\
sleep 1\n\
chmod 777 /run/munge/munge.socket.2\n\
\n\
if [ "$1" = "slurmctld" ]; then\n\
    echo "Starting slurmctld..."\n\
    exec /usr/sbin/slurmctld -D -vvv\n\
elif [ "$1" = "slurmd" ]; then\n\
    echo "Starting slurmd..."\n\
    exec /usr/sbin/slurmd -D -vvv\n\
else\n\
    exec "$@"\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
