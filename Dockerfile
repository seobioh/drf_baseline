FROM python:3.13.5-slim-bookworm

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir /server
COPY . server/
WORKDIR /server/

EXPOSE 80