FROM banyg360/wwwdatabase:base

# Source code file
COPY ./deployment/config/backup.sh /usr/local/bin/backup.sh
COPY ./deployment/docker/database/init-db.sh /docker-entrypoint-initdb.d
COPY ./deployment/docker/database/docker-entrypoint.sh /usr/local/bin/custom-docker-entrypoint.sh

COPY ./deployment/config/cronjobs /etc/cronjobs
RUN crontab -u root /etc/cronjobs && \
    chown root:root /var/spool/cron/crontabs/root && \
    chmod 600 /var/spool/cron/crontabs/root 
RUN touch /etc/crontab /etc/cron.*/*

RUN ["chmod", "+x", "/usr/local/bin/backup.sh"]
RUN ["chmod", "+x", "/docker-entrypoint-initdb.d/init-db.sh"]
RUN ["chmod", "+x", "/usr/local/bin/custom-docker-entrypoint.sh"]
RUN ["touch", "/var/log/cron.log"]


ENTRYPOINT ["custom-docker-entrypoint.sh"]
