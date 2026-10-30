FROM python:3.11.15-trixie

WORKDIR /usr/src/app

RUN apt update && apt install -y nano iputils-ping

RUN pip3 install numpy lgpio rpi-lgpio requests

COPY *.py ./

CMD ["python3", "controller.py"]
