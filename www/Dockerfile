# Dockerfile
# VPN4.one www

FROM python:3.8.5

MAINTAINER vpn4.one

RUN echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main" > /etc/apt/sources.list.d/ansible.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
RUN apt update && apt install -y sshpass ansible

COPY app /opt/vpn4one/
WORKDIR /opt/vpn4one

RUN pip install -r requirements.txt
RUN pytest

EXPOSE 8080

RUN mkdir -p /root/.ssh/
RUN echo "Host *\n    StrictHostKeyChecking no" > /root/.ssh/config
RUN chmod 400 /root/.ssh/config

CMD ["python3", "/opt/vpn4one/app.py", "--address=*"]
