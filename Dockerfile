FROM ubuntu:21.04

WORKDIR /app

RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" TZ="Europe/Moscow" apt-get install python3 python3-pip -y

COPY ./echo ./echo/
COPY ./agent_config.json .
COPY ./create_user.py .
COPY ./requirements.txt .

RUN python3 -m pip install -r requirements.txt

CMD ["uvicorn", "echo.app:app", "--host", "0.0.0.0"]
