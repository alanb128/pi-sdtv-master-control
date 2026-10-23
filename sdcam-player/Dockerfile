FROM balenalib/raspberrypi3-debian-python:latest-bookworm-build

WORKDIR /usr/src/app

ARG DEBIAN_FRONTEND=noninteractive

# Enable udevd so that plugged dynamic hardware devices show up in our container
ENV UDEV=1

RUN apt-get update && apt-get install -y python3-pil fonts-dejavu python3-rpi-lgpio mpv libmpv-dev \
    alsa-utils libgl1-mesa-dri \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade adafruit-blinka adafruit-platformdetect adafruit-circuitpython-rgb-display adafruit-circuitpython-seesaw mpv numpy

COPY *.py ./
COPY *.mp4 ./
COPY *.jpg ./
COPY entry.sh /entry.sh

RUN chmod +x /entry.sh

ENTRYPOINT ["/entry.sh"]
CMD ["python3", "/usr/src/app/con.py"]
