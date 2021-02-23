#!/usr/bin/env sh 

set -eux

trap exit TERM

if [ ! -d /etc/letsencrypt/accounts ]; then
    certbot certonly --webroot -w /var/www/certbot -d vpn4.one -d www.vpn4.one --register-unsafely-without-email --rsa-key-size 4096 --agree-tos --force-renewal
    sleep 12h & wait ${!}
fi 

while :; do certbot renew; sleep 12h & wait ${!}; done;


