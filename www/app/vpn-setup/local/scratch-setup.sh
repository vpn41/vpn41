#!/usr/bin/env bash

HOSTNAME="${1}"
PASSWORD="${2}"
USER=root
SCRIPT_DIR=$(dirname ${0})

if [ -z "${HOSTNAME}" ]; then
    echo "Target system hostname or ip address is not specified"
    exit 1
fi 

if [ -z "${PASSWORD}" ]; then
    echo "Target system ssh password is not specified"
    exit 1
fi 

ansible-playbook "${SCRIPT_DIR}/scratch-playbook.yml" --extra-vars "ansible_user=${USER} ansible_password=${PASSWORD}" -i "${HOSTNAME}", -vv
