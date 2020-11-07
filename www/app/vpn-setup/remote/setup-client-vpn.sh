#!/usr/bin/env bash

CLIENT=${1}

if [ -z "${CLIENT}" ]; then
    echo 'Usage: ./setup-client-vpn.sh CLIENT' 
    exit 1
fi 

docker-compose run --rm openvpn easyrsa build-client-full "${CLIENT}" nopass
docker-compose run --rm openvpn ovpn_getclient "${CLIENT}" > "${CLIENT}.ovpn"

