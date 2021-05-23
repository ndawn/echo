FROM node:14 as client

WORKDIR /app



FROM ubuntu:21.04

COPY . /app

RUN apt-get update
RUN apt-get install curl git nginx postgresql -y

COPY echo_nginx.conf /etc/nginx/sites-enabled

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash
RUN apt-get install nodejs

RUN git clone https://github.com/ndawn/echo-client.git /app/echo-client
RUN cd /app/echo-client
RUN npm install
RUN npm run build

RUN cd /app
RUN python -m pip install -r requirements.txt

CMD ["uvicorn app:app"]
