#!/usr/bin/env bash

HOSTNAME="${1}"
PASSWORD="${2}"
USER=root
PORT="${3:-38944}"
SCRIPT_DIR=$(dirname ${0})

if [ -z "${HOSTNAME}" ]; then
    echo "Target system hostname or ip address is not specified"
    exit 1
fi 

if [ -z "${PASSWORD}" ]; then
    echo "Target system ssh password is not specified"
    exit 1
fi 

ansible-playbook "${SCRIPT_DIR}/server-playbook.yml" --extra-vars "hostname=${HOSTNAME} server_port=${PORT}" \
    --extra-vars "ansible_user=${USER} ansible_password=${PASSWORD}" \
    --ssh-common-args "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
    -i "${HOSTNAME}", -vv
