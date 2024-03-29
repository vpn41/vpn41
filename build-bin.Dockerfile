FROM python:3.10

MAINTAINER Vpn4.One

COPY app /tmp/vpn4one/
WORKDIR /tmp/vpn4one/
RUN pip install -r requirements.txt
RUN pip install pyinstaller
RUN mkdir /dist

RUN pytest
CMD pyinstaller --add-data templates/:templates/ --add-data static/:static/ --add-data vpn-setup/:vpn-setup/ --onefile app.py && cp -v dist/app /dist/vpn41

