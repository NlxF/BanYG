#!/bin/bash
set -e

HOME=/www/BanYG

echo "edit flask plugin compatible with flask 1.0.2"
packages=($(python3 -c "import site; print(site.getsitepackages())" | tr -d "[],\'\'"))
for package in ${packages[@]}; do
    cache_path=${package}'/flask_cache/jinja2ext.py'
    echo 'search flask_cache at: '${cache_path}
    if [ -f ${cache_path} ]; then
        echo "find flask_cache, sed to compatible with flask 1.0.2"
        sed -i 's/^from flask.ext.cache /from flask_cache /g' ${cache_path}
    fi

    flask_migrate_path=${package}'/flask_migrate/templates/script.py.mako'
    echo 'search flask_migrate at: '${flask_migrate_path}
    if [ -f ${flask_migrate_path} ]; then
        echo "find flask_migrate, sed to compatible with BanYG"
        sed -i 's/^import sqlalchemy as sa /import sqlalchemy as sa \\\n import bwg360 /g' ${flask_migrate_path}
        # cp ${HOME}'/translations/zh/LC_MESSAGES/flask_user.po' ${package}'/flask_user/translations/zh/LC_MESSAGES'
        # cp ${HOME}'/translations/zh/LC_MESSAGES/flask_user.mo' ${package}'/flask_user/translations/zh/LC_MESSAGES'
    fi

    youtube_dl_path=${package}'/youtube_dl/extractor/youtube.py'
    echo 'search youtube_dl at: '${youtube_dl_path}
    if [ -f ${youtube_dl_path} ]; then
        echo "find youtube_dl, sed to compatible with BanYG"
        rm ${youtube_dl_path}
        cp ${HOME}'/plugins/youtube.py' ${package}'/youtube_dl/extractor/'
    fi
done

if [ ! -f '/var/lib/mysql/init' ]; then

    # echo "Initialize or Update DB..."
    cd ${HOME}/
    # echo $(python3 manager.py db minit)
    # echo $(python3 manager.py db mmigrate -m "init or update")
    # echo $(python3 manager.py db mupgrade)

    echo "Initialize default data..."
    echo $(python3 manager.py create_db)

    # echo "Add log slice conf"
    # /usr/sbin/logrotate -f /etc/logrotate.d/nginx    // 未到时间或者未到切割条件，强制切割
    # /usr/sbin/logrotate -d -f /etc/logrotate.d/nginx // 输出切割debug信息
    # /usr/sbin/logrotate -f /etc/logslice.conf

    echo $(touch '/var/lib/mysql/init')
fi

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
    echo "No directory to recovery..."
fi

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