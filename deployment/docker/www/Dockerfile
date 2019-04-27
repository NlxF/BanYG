FROM banyg360/wwwserver:base

ENV HOME=/www/BanYG

# install python, and supervisord, redis-server
RUN apt-get update && apt-get install -y python3 supervisor uwsgi python3-pip procps redis-server wget logrotate && \
    /usr/bin/pip3 install uwsgi flask==1.0.2 Flask-User

# Source code file
COPY ./manager.py ${HOME}/
COPY ./runserver.py ${HOME}/
COPY ./celery_worker.py ${HOME}/
COPY ./cookies.txt ${HOME}/
COPY ./bwg360 ${HOME}/bwg360
COPY ./deployment/plugins ${HOME}/plugins
# COPY ./deployment/config/translations ${HOME}/
# COPY ./deployment/data/ ${HOME}/sql/

COPY ./deployment/config/wait-for-it.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-it.sh

COPY ./requirements.txt ${HOME}/
RUN cd ${HOME} && \
   /usr/bin/pip3 install -r requirements.txt

# Copy the nginx configuration file from the current directory and paste 
COPY ./deployment/config/nginx.conf /etc/nginx/nginx.conf
COPY ./deployment/config/nginx-server.conf /etc/nginx/conf.d/
RUN touch /var/log/nginx/stdout.log && touch /var/log/nginx/stderr.log && touch /var/log/nginx/www.BanYG.log

# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY ./deployment/config/uwsgi.ini /etc/uwsgi/apps-available/uwsgi.ini
RUN ln -s /etc/uwsgi/apps-available/uwsgi.ini /etc/uwsgi/apps-enabled/uwsgi.ini
RUN touch /var/log/uwsgi/stdout.log && touch /var/log/uwsgi/stderr.log

COPY ./deployment/config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN touch /var/log/supervisor/supervisord.log

COPY ./deployment/config/redis.conf /etc/redis/redis.conf
RUN touch /var/log/redis/stdout.log && touch /var/log/redis/stderr.log

# COPY ./deployment/config/logslice.conf /etc/logrotate.d/

# setup entrypoint
COPY ./deployment/docker/www/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# https://github.com/moby/moby/issues/31243#issuecomment-406879017
RUN ln -s /usr/local/bin/docker-entrypoint.sh / && \
    chmod 777 /usr/local/bin/docker-entrypoint.sh && \
    chgrp -R 0 /usr/local/bin/docker-entrypoint.sh && \
    chown -R nginx:root /usr/local/bin/docker-entrypoint.sh

# https://docs.openshift.com/container-platform/3.3/creating_images/guidelines.html
RUN chgrp -R 0 /var/log /var/cache /run/pid /spool/nginx /var/run /run /tmp /etc/uwsgi /etc/nginx && \
    chmod -R g+rwX /var/log /var/cache /run/pid /spool/nginx /var/run /run /tmp /etc/uwsgi /etc/nginx && \
    chown -R nginx:root ${HOME} && \
    chmod -R 777 ${HOME} /etc/passwd
