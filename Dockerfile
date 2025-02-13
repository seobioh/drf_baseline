FROM python:3.9-slim

RUN pip install gunicorn
RUN pip install python-dotenv
RUN pip install djangorestframework
RUN pip install djangorestframework-simplejwt
RUN pip install django-cors-headers

RUN mkdir /server

COPY . server/

WORKDIR /server/

EXPOSE 80