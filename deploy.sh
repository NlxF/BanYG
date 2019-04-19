#!/bin/bash
#
# 服务端部署
# 命令格式：
# 1. ./deploy.sh start  启动主服务(www、database)
# 2. ./deploy.sh stop   停止服务
# 3. ./deploy.sh restart 重启服务
# 4. ./deploy.sh pull serverName1, [serverName2...] 拉取远程仓库的更新

set -e

all_services=("www-server" "www-database")
DomainName='banyg360/'
argc=$#
argv=($@)

function startServers(){
    docker-compose -f docker-compose-prod.yml up -d
}

function stopServers(){
    docker-compose -f docker-compose-prod.yml down
}

function nanualBackup(){
    database_container=$(docker container ls --filter ancestor=$DomainName'www-database:latest' --format "{{.ID}}")
    if [[ ${#database_container[@]} -eq 0 ]]; then
        echo "2.www-database镜像未运行."
    else 
        local idx=0
        for db in ${database_container}; do
            echo "    "${idx}".备份数据库:"${db}
            docker exec -i -t ${db} /bin/sh -c "/usr/local/bin/backup.sh"
            ((idx+=1))
        done
    fi
}

function upgrade(){
    local argc=$#
    local num=0
    if [[ ${argc} > 0 ]]; then
        echo "    "${num}".停止服务:"
        ((num+=1))
        stopServers
        echo "    "${num}".更新镜像:"
        ((num+=1))
        for ((idx=1; idx<argc; ++idx)); do
            if [[ ${all_services[@]} =~ ${argv[idx]} ]]; then
                echo "    "${num}".镜像:"$DomainName${argv[idx]}
                docker image rm -f $DomainName${argv[idx]}
                docker-compose -f docker-compose-prod.yml pull ${argv[idx]}
                if [ "www-database" == ${argv[idx]} ]; then
                    if [ -d ./volume/var/ ]; then
                        rm -rf ./volume/var/
                    fi
                fi
            else
                echo "    "${num}".镜像:"$DomainName${argv[idx]}" 不存在."
            fi
            ((num+=1))
        done
        echo "    "${num}".更新结束!"
    fi
}

if [[ ${argc} > 0 ]]; then
    if [ ${argv[0]} == "start" ]; then
        echo "1.启动服务:"
        startServers
    elif [ ${argv[0]} == "stop" ]; then
        echo "1.停止服务:"
        stopServers
    elif [ ${argv[0]} == "restart" ]; then
        echo "1.重启服务:"
        stopServers
        startServers
    elif [ ${argv[0]} == "backup" ]; then
        echo "1.备份服务:"
        nanualBackup
    elif [ ${argv[0]} == "pull" ]; then
        echo "1.更新服务:"
        upgrade ${argv[@]}
    else
        echo "1.未知命令:"${argv}
    fi
else
    echo "1.无效命令"
fi