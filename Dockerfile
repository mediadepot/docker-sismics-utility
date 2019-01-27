FROM python:3-alpine3.8

COPY /rootfs /

RUN pip install requests pyyaml