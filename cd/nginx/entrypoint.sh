#!/usr/bin/env -S bash -eux

if [ ! -d /etc/letsencrypt/live ]; then
    mv /etc/nginx/conf.d/www.conf /etc/nginx/conf.d/www.conf~
    (sleep 1m & wait "${!}"; nginx -s stop) &
    nginx -g "daemon off;"
    mv /etc/nginx/conf.d/www.conf~ /etc/nginx/conf.d/www.conf
elif [ -f /etc/nginx/conf.d/www.conf~ ]; then
    mv /etc/nginx/conf.d/www.conf~ /etc/nginx/conf.d/www.conf
fi

while :; do sleep 6h & wait "${!}"; nginx -s reload; done & nginx -g "daemon off;"
