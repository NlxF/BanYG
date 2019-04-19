#!/bin/bash

echo "Running cron task manager..."
/etc/init.d/cron start
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to start cron: $status"
    exit $status
fi

/usr/local/bin/docker-entrypoint.sh mysqld

echo "Done!"
