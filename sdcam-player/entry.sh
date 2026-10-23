#!/bin/bash

# Keep forcing the analog interface engine awake before python boots
echo "on" > /sys/class/drm/card0-Composite-1/status || true
export UDEV=1 

# mpv command line example:
#mpv --vo=gpu --gpu-context=drm --drm-connector=Composite-1 --hwdec=mmal-copy \
#   --ao=alsa --audio-device=alsa/hw:Headphones --no-terminal "$@" 

# Hand execution off cleanly to the python engine specified in the Dockerfile CMD
exec "$@"
