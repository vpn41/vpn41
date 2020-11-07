#!/usr/bin/env bash

HOSTNAME="${1}"
PASSWORD="${2}"
FETCH_KEYS="${3}"
PLATFORM="${4}"
USER=root
PORT="${5:-38944}"
SCRIPT_DIR=$(dirname ${0})

print_err_then_exit() {
    echo "${1}"
    echo "usage: ./client-setup.sh HOSTNAME PASSWORD FETCH_KEYS PLATFORM"
    exit 1
}

if [ -z "${HOSTNAME}" ]; then
    print_err_then_exit "Target system hostname or ip address is not specified"
fi

if [ -z "${PASSWORD}" ]; then
    print_err_then_exit "Target system ssh password is not specified"
fi

if [ -z "${FETCH_KEYS}" ]; then
    print_err_then_exit "Specify whether to fetch keys, {yes|no|true|false|1|0} accepted"
fi

if [ -z "${PLATFORM}" ]; then
    print_err_then_exit "No platform specified"
fi


ansible-playbook "${SCRIPT_DIR}/client-playbook.yml" --extra-vars "fetch_keys=${FETCH_KEYS} platform=${PLATFORM} server_port=${PORT}" \
    --extra-vars "ansible_user=${USER} ansible_password=${PASSWORD}" -i "${HOSTNAME}", -vv
