FROM nginx
MAINTAINER vpn4.one

COPY www.conf /etc/nginx/conf.d/
COPY acme.conf /etc/nginx/conf.d/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
