#!/usr/bin/env bash

CLIENT_NUM="${1}"
PLATFORM="${2}"
export REMOTE_PORT="${3}"
NOW=$(date -u +%F-%H-%M-%S)
OUT_DIR="${HOME}/myvpn/${NOW}"

if [ -z "${CLIENT_NUM}" ] || [ -z "${PLATFORM}" ]; then
    echo 'Usage: ./setup-multiple-clients.sh CLIENT_NUM PLATFORM'
    exit 1
fi

mkdir -p "${OUT_DIR}"

echo "Generating ${CLIENT_NUM} key(s) in ${OUT_DIR}..."

add_platform_options() {
    local platform="${1}"
    local fn="${2}"

    if [ "${platform}" == 'linux' ]; then
        {
            echo 'script-security 2'
            echo 'up /etc/openvpn/update-resolv-conf'
            echo 'down /etc/openvpn/update-resolv-conf'
        } >> "${fn}"
    fi
}

for (( i = 0; i < CLIENT_NUM; i++ ))
do
    CLIENT_FN=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 8 | head -n 1)
    FULL_FN="${OUT_DIR}/${CLIENT_FN}.ovpn"
    docker-compose run --rm openvpn easyrsa build-client-full "${CLIENT_FN}" nopass
    docker-compose run --rm openvpn ovpn_getclient "${CLIENT_FN}" > "${FULL_FN}"
    add_platform_options "${PLATFORM}" "${FULL_FN}"
done

if [ -d "${OUT_DIR}" ]; then
    LATEST="${HOME}/myvpn-${NOW}.zip"
    zip -r "${LATEST}" "${OUT_DIR}"
    ln -sf "${LATEST}" ~/myvpn.zip
fi

#if [ -d "${OUT_DIR}" ]; then
#    LATEST="${HOME}/myvpn-${NOW}.tar.gz"
#    tar czvf "${LATEST}" "${OUT_DIR}"
#    ln -sf "${LATEST}" ~/myvpn.tar.gz
#fi
