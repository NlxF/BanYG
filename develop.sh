#!/bin/bash
#
# 本地构建、升级、提交本地镜像。
# 命令格式：
# 1. ./develop.sh init  初始化本地镜像，此命令需为第一条运行的命令 
# 2. ./develop.sh rebuild  重建本地镜像
# 3. ./develop.sh upgrade [serverName1, [serverName2...]] 升级指定的服务
# 4. ./develop.sh commit [serverName1, [serverName2...]] 提交本地更新到远程仓库
# 5. ./develop.sh base 构建基础镜像，避免频繁更新浪费时间
#

set -e

all_services=("www-server" "www-database")
DomainName='banyg360/'

argc=$#
argv=($@)
declare -a all_images

function stopContainer(){
    docker-compose -f docker-compose.yml down
}

function clearExistImages(){
    # clear exists images
    local idx=0
    all_images=$(docker image ls --format "{{.Repository}}")
    for image in ${all_images}; do
        for service in ${all_services[@]}; do
            if [ $DomainName${service} == ${image} ]; then
                echo "    "${idx}".移除镜像: "${image}
                docker image rm -f ${image}
                ((idx+=1))
            fi
        done
    done
}

function init(){
    echo "2.停止运行镜像"
    stopContainer
    echo "3.开始更新镜像:"
    clearExistImages

    local idx=4
    # if [ $1x == "rebuild"x ]
    # then
        
    # fi
    echo ${idx}".构建主服务镜像:"
    docker-compose -f docker-compose.yml build
}

function rebuild(){
    init rebuild
}

function initTest(){
    all_images=$(docker image ls --format "{{.Repository}}")
    if [[ ${all_images[@]} =~ $DomainName${all_services[0]} ]] && \
       [[ ${all_images[@]} =~ $DomainName${all_services[1]} ]]
    then
        return 0
    fi

    echo "2.环境未初始化, 请先运行init命令初始化环境."
    return 1
}

function upgrade(){
    initTest
    if [[ $? -eq 1 ]]; then
        exit 1
    fi
    
    local argc=$#
    if [[ ${argc} -eq 0 ]]; then
        echo "2.未指定需要升级的镜像."
        exit 1
    fi
    echo "2.开始更新本地镜像:"
    local num=0
    local argv=($@)
    for ((idx=0; idx<argc; ++idx)); do
        if [[ ${all_services[@]} =~ ${argv[idx]} ]]; then
            echo "    "${num}".更新主镜像:"$DomainName${argv[idx]}
            docker image rm -f $DomainName${argv[idx]}
            docker-compose build ${argv[idx]}
        else
            echo "    "${num}".指定更新镜像:"$DomainName${argv[idx]}"本地不存在."
        fi
        ((num+=1))
    done
}

function commit(){
    initTest
    if [[ $? -eq 1 ]]; then
        exit 1
    fi

    local argc=$#
    if [[ ${argc} -eq 0 ]]; then
        echo "2.未指定需要上传的远程镜像."
        exit 1
    fi

    local argv=($@)
    for ((idx=0; idx<argc; ++idx)); do
        if [[ ${all_services[@]} =~ ${argv[idx]} ]]; then
            echo "    "${idx}".本地镜像:"$DomainName${argv[idx]}
            docker push $DomainName${argv[idx]}":latest"
        else
            echo "    "${idx}".指定上传镜像:"$DomainName${argv[idx]}"本地不存在."
        fi
    done
}

function base(){
    local idx=0
    base_images=$(docker image ls --filter=reference='$DomainName*:base' --format "{{.ID}}")
    for image in ${base_images}; do
        echo "    "${idx}".移除缓存的基础镜像:"${image}
        docker image rm -f ${image}
        ((idx+=1))
    done

    echo "    "${idx}".构建database服务基础镜像"
    docker build --no-cache -f ./deployment/docker/database/Dockerfile.Base -t $DomainName'wwwdatabase:base' .
    ((idx+=1))
    echo "    "${idx}".构建server基础镜像"
    docker build --no-cache -f ./deployment/docker/www/Dockerfile.Base -t $DomainName'wwwserver:base' .
}

if [[ ${argc} > 0 ]]; then
    if [ ${argv[0]} == "init" ]; then
        echo "1.初始化镜像:"
        init
    elif [ ${argv[0]} == "rebuild" ]; then
        echo "1.开始重构镜像:"
        init rebuild
    elif [ ${argv[0]} == "upgrade" ]; then
        echo "1.准备更新本地镜像."
        upgrade ${argv[@]:1:argc-1}
    elif [ ${argv[0]} == "commit" ]; then
        echo "1.更新远程镜像:"
        commit ${argv[@]:1:argc-1}
    elif [ ${argv[0]} == "base" ]; then
        echo "1.构建基础镜像:"
        base
    else
        echo "1.未知命令:"${argv}
    fi
else
    echo "1.无效命令"
fi