# Executable building Dockerfile
# VPN4.one www

FROM python:3.8.5

MAINTAINER vpn4.one

COPY app /tmp/vpn4one/
WORKDIR /tmp/vpn4one/
RUN pip install -r requirements.txt
RUN pip install pyinstaller
RUN mkdir /dist

RUN pytest
CMD pyinstaller --add-data templates/:templates/ --add-data static/:static/ --add-data vpn-setup/:vpn-setup/ --onefile app.py && cp -v dist/app /dist/vpn41

