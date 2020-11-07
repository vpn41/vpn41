#!/usr/bin/env bash

REMOTE_HOST="${1}"
export REMOTE_PORT="${2}"

if [ -z "${REMOTE_HOST}" ] || [ -z "${REMOTE_PORT}" ]; then
    echo 'Usage: ./setup-server-vpn.sh REMOTE_HOST REMOTE_PORT'
    exit 1
fi 

docker-compose stop

if [ -d "${HOME}/openvpn-data" ]; then
    NOW=$(date -u +%F-%H-%M-%S)
    SUFFIX=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 8 | head -n 1)
    echo 'Backing up prev config...'
    mv "${HOME}/openvpn-data" "${HOME}/openvpn-data.${NOW}.${SUFFIX}"
fi

check_last_result() {
    if [ ${?} -ne 0 ]; then
        echo "${1}"
        exit 1
    fi
}

docker-compose run --rm openvpn ovpn_genconfig -u "udp://${REMOTE_HOST}:${REMOTE_PORT}" -C AES-256-CBC -n 208.67.222.222 -n 208.67.220.220
check_last_result 'Server configuration error, exit'

echo "myvpn" | docker-compose run --rm openvpn ovpn_initpki nopass
check_last_result 'Init pki error, exit'

docker-compose up -d
check_last_result 'OpenVPN start error, exit'


