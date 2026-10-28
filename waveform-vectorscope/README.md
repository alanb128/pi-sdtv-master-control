# Scope/audio/video monitor

This is the folder for the waveform monitor/vectorscope/vu meter.

Parts:

Touch screen: [ELECROW 5 Inch Touch Screen Monitor for Raspberry Pi 800×480 LCD Display](https://www.amazon.com/dp/B07FDYXPT7)

Tactile push buttons: [Adafruit assortment](https://www.adafruit.com/product/1010), and others

Pi fans: https://www.printables.com/model/328676-raspberry-pi-4-fan-mount-backward-compatible/files

Configuration settings for the Pi 4:
```
Device GPU memory in megabytes: 64
Define DT overlays: "vc4-kms-v3d,composite=1,cma-320","gpio-key,gpio=4,keycode=28,label=ENTER,gpio_pull=up,active_low=1","gpio-key,gpio=18,keycode=15,label=TAB,gpio_pull=up,active_low=1"
Custom configuration:
BALENA_HOST_CONFIG_enable_tvout: 1
BALENA_HOST_CONFIG_sdtv_mode: 0
```
