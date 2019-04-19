#!/bin/bash
set -e

HOME=/www/BanYG

echo "edit flask plugin compatible with flask 1.0.2"
packages=($(python -c "import site; print(site.getsitepackages())" | tr -d "[],\'\'"))
for package in ${packages[@]}; do
    cache_path=${package}'/flask_cache/jinja2ext.py'
    echo 'search flask_cache at: '${cache_path}
    if [ -f ${cache_path} ]; then
        echo "find flask_cache, sed to compatible with flask 1.0.2"
        sed -i 's/^from flask.ext.cache /from flask_cache /g' ${cache_path}
        break
    fi
    sqlalchemy_cache_path=${package}'/flask_sqlalchemy_cache/core.py'
    echo 'search flask_sqlalchemy_cache at: '${sqlalchemy_cache_path}
    if [ -f ${sqlalchemy_cache_path} ]; then
        echo "find flask_sqlalchemy_cache, sed to compatible with flask 1.0.2"
        sed -i 's/^from flask.ext.sqlalchemy /from flask_sqlalchemy /g' ${sqlalchemy_cache_path}
        break
    fi
done

# echo "Add log slice conf"
# /usr/sbin/logrotate -f /etc/logrotate.d/nginx    // 未到时间或者未到切割条件，强制切割
# /usr/sbin/logrotate -d -f /etc/logrotate.d/nginx // 输出切割debug信息
# /usr/sbin/logrotate -f /etc/logslice.conf

if [ -d '${HOME}/restore/' ]; then
    SQLLIST=`ls ${HOME}/restore/`
    if [ ${#SQLLIST[@]}>0 ]; then
        echo "Data recovery..."
        for file in ${SQLLIST}; do 
            if [ -f ${HOME}/sql/$file ]; then
                echo "    Recovery sql file:"$file
                mysql -h www-database -u root -p$MYSQL_ROOT_PASSWORD BanYG < ${HOME}/sql/$file
            fi
        done
    else
        echo "No data to recovery..."
    fi
else
    echo "No recovery directory..."
fi

echo "Initialize or Update DB..."
cd ${HOME}/
echo $(python manager.py db init)
echo $(python manager.py db migrate -m "init or update")
echo $(python manager.py db upgrade)

echo "Initialize default data..."
echo $(python manager.py init_data)

echo "start supervisord..."
# if the running user is an Arbitrary User ID
if ! whoami &> /dev/null; then
    # make sure we have read/write access to /etc/passwd
    if [ -w /etc/passwd ]; then
        # write a line in /etc/passwd for the Arbitrary User ID in the 'root' group
        echo "${USER_NAME:-default}:x:$(id -u):0:${USER_NAME:-default} user:${HOME}:/sbin/nologin" >> /etc/passwd
    fi
fi

if [ "$1" = 'supervisord' ]; then
    exec /usr/bin/supervisord
fi

exec "$@"