#!/usr/bin/env sh

tar kxf /tmp/etc.letsencrypt.tar.gz -C /
trap exit TERM; while :; do certbot renew; sleep 12h & wait ${!}; done;
