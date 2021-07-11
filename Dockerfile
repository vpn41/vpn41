FROM python:3.8.5

MAINTAINER Vpn4.One

RUN echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main" > /etc/apt/sources.list.d/ansible.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
RUN apt-get update && apt-get install -y sshpass ansible

COPY app/requirements.txt /opt/vpn4one/
WORKDIR /opt/vpn4one
RUN pip install -r requirements.txt

RUN mkdir -p /root/.ssh/
RUN echo "Host *\n    StrictHostKeyChecking no" > /root/.ssh/config
RUN chmod 400 /root/.ssh/config

EXPOSE 8080

COPY app /opt/vpn4one/
RUN pytest

CMD ["python3", "/opt/vpn4one/app.py", "--address=*"]
