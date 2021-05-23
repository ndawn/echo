FROM node:14 as client

WORKDIR /app

COPY ./client .

RUN npm install
RUN npm run build

FROM ubuntu:21.04

WORKDIR /app

COPY --from=client /app/dist ./client/dist/

RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" TZ="Europe/Moscow" apt-get install curl python3 python3-pip nginx postgresql -y

COPY ./echo_nginx.conf /etc/nginx/sites-enabled
RUN rm /etc/nginx/sites-enabled/default

RUN service nginx restart

COPY ./echo ./echo/
COPY ./requirements.txt .

RUN python3 -m pip install -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "echo.app:app"]
