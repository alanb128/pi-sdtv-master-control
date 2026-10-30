import RPi.GPIO as GPIO
import os
import requests
import time

video_out = 1
mode = "home"

def button_press(channel):
    global mode
    print("Button {} pressed.".format(channel))
    if channel == 17:
        mode = "home"
        print("Sending {} URL to browser.".format(mode))
        r = requests.post('http://browser:5011/url/', data={'url': 'http://webserver'})
        print("Response from browser: {}".format(r.status_code))
     
    else:
        if channel == 26:
            mode = "waveform"
            
        if channel == 19:
            mode = "vectorscope"
            
        if channel == 13:
            mode = "video_vu"
            
        if channel == 6:
            mode = "vumeter"
        
        if channel == 27:
            if mode[:8] == "waveform":
                mode = "waveform?mode=chroma"
            
        if channel == 22:
            if mode[:8] == "waveform":
                mode = "waveform?mode=luma"
        
        print("Sending {} URL to browser.".format(mode))
        r = requests.post('http://browser:5011/url/', data={'url': 'http://webserver/' + mode})
        print("Response from browser: {}".format(r.status_code))
    
    
def input_change(channel):
    global video_out
    print("Input button (channel {}) pressed.".format(channel))
    video_out = video_out + 1
    if video_out == 5:
        video_out = 1
    set_video_LED(video_out)

def set_video_LED(vid):
        if video_out == 1:
            GPIO.output(12, 1)
            GPIO.output(16, 0)
            GPIO.output(20, 0)
            GPIO.output(21, 0)
        elif video_out == 2:
            GPIO.output(12, 0)
            GPIO.output(16, 1)
            GPIO.output(20, 0)
            GPIO.output(21, 0)
        elif video_out == 3:
            GPIO.output(12, 0)
            GPIO.output(16, 0)
            GPIO.output(20, 1)
            GPIO.output(21, 0)
        else:
            GPIO.output(12, 0)
            GPIO.output(16, 0)
            GPIO.output(20, 0)
            GPIO.output(21, 1)
            
print("Starting controller...")

GPIO.setmode(GPIO.BCM)

#### Set buttons input
# Home button
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(17, GPIO.FALLING, callback=button_press, bouncetime=300)
# WF button
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(26, GPIO.FALLING, callback=button_press, bouncetime=300)
# VS button
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(19, GPIO.FALLING, callback=button_press, bouncetime=300)
# PIC button
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(13, GPIO.FALLING, callback=button_press, bouncetime=300)
# VU button
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(6, GPIO.FALLING, callback=button_press, bouncetime=300)
# input button
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(10, GPIO.FALLING, callback=input_change, bouncetime=300)
# option A button
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.FALLING, callback=button_press, bouncetime=300)
# option B button
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.FALLING, callback=button_press, bouncetime=300)

## gpio outputs
GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

# Set initial LED state
set_video_LED(video_out)


while True:
    time.sleep(1)
