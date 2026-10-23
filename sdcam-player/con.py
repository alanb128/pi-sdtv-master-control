import sys
import time
import board
import digitalio
import numpy as np
import mpv
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735
import RPi.GPIO as GPIO
from adafruit_seesaw import seesaw, rotaryio
from pathlib import Path
import os

# --- Shared Media State Variables ---
latest_time_pos = 0.0
duration = 0.0
is_paused = False
playlist_pos = 1
playlist_count = 1
fps = 24.0  

#### Settings ####

try:
    ast = int(os.getenv('AUTO_START', '1'))
except Exception as e:
    print("Invalid value for AUTO_START. Using default 1.")
    ast = 0
if ast == 1:
    AUTO_START = True
else:
    AUTO_START = False

try:
    ast = int(os.getenv('AUTO_REPEAT', '1'))
except Exception as e:
    print("Invalid value for AUTO_REPEAT. Using default 1.")
    ast = 0
if ast == 1:
    AUTO_REPEAT = True
else:
    AUTO_REPEAT = False

BOUNCE_TIME = 300
FILE_PATH = Path("/usr/src/app")
player_mode = "stop"  # or play
jogging = False
rotary_pos = 0  # keeps track of wheel position

# --- MPV Property Observers ---
def on_time_pos_change(name, value):
    global latest_time_pos
    if value is not None:
        latest_time_pos = value
    else:
        latest_time_pos = 0.0

def on_duration_change(name, value):
    global duration
    if value is not None:
        duration = value

def on_pause_change(name, value):
    global is_paused
    if value is not None:
        is_paused = value

def on_playlist_pos_change(name, value):
    global playlist_pos
    if value is not None:
        playlist_pos = value + 1

def on_playlist_count_change(name, value):
    global playlist_count
    if value is not None:
        playlist_count = value
        print("Playlist count: {}".format(playlist_count))

def on_fps_change(name, value):
    global fps
    if value is not None and value > 0:
        fps = value

def on_end_file(name, value):
    global player_mode
    #print("Event")
    #if value is not None and value > 0:
    #print("End File count {} pos {}".format(player.playlist_count, player.playlist_pos))
    if (player.playlist_count > 0) and (player.playlist_pos == -1):
        print("Playlist end reached.")
        if AUTO_REPEAT:
            print("Reloading playlist (AUTO_REPEAT=True)")
            make_playlist()
        else:
            player_mode = "stop"
            GPIO.output(12, GPIO.LOW)
        
# --- Various functions for handling
def make_playlist():

    global player
    
    # make a playlist of all mp3 files in FILE_PATH
    mp4_files = [str(file.resolve()) for file in FILE_PATH.glob("*") if file.suffix.lower() == ".mp4"]

    if not mp4_files:
        print(f"No .mp4 files found in {folder_path}")
    else:
        print(f"Loading {len(mp4_files)} files into the mpv interface...")
        
        # 4. Queue up the files natively
        for index, video_path in enumerate(mp4_files):
            if index == 0:
                if AUTO_START:
                    # Play the first file immediately to initialize playback
                    player.play(video_path)
                else:
                    player.playlist_append(video_path)
            else:
                # Append the remaining files to the underlying libmpv playlist queue
                player.playlist_append(video_path)

def display_button(channel):
    print("Display button {} pressed.".format(channel))
    if channel == 17:
        player.stop()
        player_mode = "stop"
        GPIO.output(12, GPIO.LOW)
        player.play("bars.jpg")
    elif channel == 18:
        player.stop()
        player_mode = "stop"
        GPIO.output(12, GPIO.LOW)
        player.play("station-id.jpg")
def playback_button(channel):
    global player, player_mode

    print("Playback button {} pressed.".format(channel))
    if channel == 22:   # play
        if player_mode != "play":
            player_mode = "play"
            GPIO.output(12, GPIO.HIGH)
            if player.playlist_count == 0:
                make_playlist()
            player.playlist_pos = 0 # start playlist from begining
    elif channel == 5:  # stop
        #if player_mode == "play":
        player.command("stop")
        GPIO.output(12, GPIO.LOW) 
        player_mode = "stop"
    elif channel == 27:  # prev
        if player_mode == "play":
            player.command('playlist_prev')
        else:
            #todo: playlist counter move before playing
            pass
    elif channel == 23:  # next
        if player_mode == "play":
            player.command('playlist_next')
        else:
            #todo: playlist counter move before playing
            pass

def power_button(channel):
    print("Power button pressed on {}.".format(channel))
    GPIO.output(14, not GPIO.input(14)) 

def rotary_incoming(channel):
    print("Rotary data present on {}.".format(channel))

    # Triggered by rotary QT interrupt
    # when rotary wheel is turned or clicked
    #
    global rotary_pos
    current_pos = seesaw.encoder_position()
    rot_btn = not(seesaw.digital_read(24))
    if rotary_pos == current_pos:
        if rot_btn == True:
            # Add code here for rotary button press
            pass
    else:
        if current_pos < rotary_pos:
            print("Turned left {}".format(current_pos))
            # Action on every other (even) click
            if (current_pos % 2) == 0:
                if player_mode == "play":
                    if jogging:
                        if (current_pos % 4) == 0:
                            player.command('frame_back_step')
                    else:
                        if current_pos > 6:
                            player.speed = 3
                        else:
                            if current_pos < 0:
                                player.speed = 1
                            else:
                                player.speed = current_pos * 0.5
               
        else:
            print("Turned right {}".format(current_pos))
            # Action on every other (even) click
            if (current_pos % 2) == 0:
                if player_mode == "play":
                    if jogging:
                        if (current_pos % 4) == 0:
                            player.command('frame_step')
                    else:
                        if current_pos > 6:
                            player.speed = 3
                        else:
                            if current_pos < 0:
                                player.speed = 1
                            else:
                                player.speed = current_pos * 0.5
    rotary_pos = current_pos

def jog_button(channel):
    global jogging, player, player_mode
    
    if not jogging:
        # in jog mode
        print("Jog pressed on {}.".format(channel))
        if player_mode == "play":
            jogging = True
            GPIO.output(6, GPIO.HIGH)
            player_mode == "pause"
            player.pause = True
    else:
        print("Jog mode off")
        GPIO.output(6, GPIO.LOW)
        player_mode = "play"
        jogging = False
        player.pause = False

GPIO.setmode(GPIO.BCM)

# Set button inputs
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(4, GPIO.FALLING, callback=display_button, bouncetime=BOUNCE_TIME)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(17, GPIO.FALLING, callback=display_button, bouncetime=BOUNCE_TIME)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(18, GPIO.FALLING, callback=display_button, bouncetime=BOUNCE_TIME)

GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.FALLING, callback=playback_button, bouncetime=BOUNCE_TIME)

GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.FALLING, callback=playback_button, bouncetime=BOUNCE_TIME)

GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(23, GPIO.FALLING, callback=playback_button, bouncetime=BOUNCE_TIME)

GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(5, GPIO.FALLING, callback=playback_button, bouncetime=BOUNCE_TIME)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(21, GPIO.FALLING, callback=power_button, bouncetime=BOUNCE_TIME)

GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(13, GPIO.FALLING, callback=jog_button, bouncetime=BOUNCE_TIME)

# rotary interrupt
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(16, GPIO.FALLING, callback=rotary_incoming, bouncetime=30)

# Outputs
GPIO.setup(14, GPIO.OUT) # power LED
GPIO.setup(19, GPIO.OUT) # rem LED
GPIO.setup(12, GPIO.OUT) # play LED
GPIO.setup(6, GPIO.OUT) # jog LED

# Default LED values
GPIO.output(14, GPIO.LOW) 
GPIO.output(19, GPIO.LOW) 
GPIO.output(12, GPIO.LOW) 
GPIO.output(6, GPIO.LOW)

# Adafruit I2C QT Rotary Encoder
# Using the INT output on Pi GPIO 16
try:
    seesaw = seesaw.Seesaw(board.I2C(), addr=0x36)
except:
    print("Error initializing the rotary encoder board.")
    USE_ROTARY = False
else:
    seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
    print("Found seesaw supported product {}".format(seesaw_product))
    if seesaw_product != 4991:
        print("Wrong firmware loaded for QT encoder?  Expected 4991")
    # Set up the rotary click button, and add to interrupt
    seesaw.pin_mode(24, seesaw.INPUT_PULLUP)  # Pin on the QT
    seesaw.set_GPIO_interrupts(1 << 24, True)
    seesaw.enable_encoder_interrupt()


# --- Initialize MPV Player ---
#player = mpv.MPV(video=False)
player = mpv.MPV(
    vo="gpu",
    gpu_context="drm",
    drm_connector="Composite-1",
    hwdec="mmal-copy",
    ao="alsa",
    audio_device="alsa/hw:Headphones",
    terminal=False  # Replaces --no-terminal
)

player['image-display-duration'] = 'inf'  # player set to display still images indefintely
player.observe_property("time-pos", on_time_pos_change)
player.observe_property("duration", on_duration_change)
player.observe_property("pause", on_pause_change)
player.observe_property("playlist-pos", on_playlist_pos_change)
player.observe_property("playlist-count", on_playlist_count_change)
player.observe_property("container-fps", on_fps_change)
player.observe_property("eof-reached", on_end_file)

# --- Hardware & TFT Setup ---
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

spi = board.SPI()

display = st7735.ST7735R(
    spi, rotation=270, x_offset=2, y_offset=3, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=24000000
)

width, height = 128, 128
image = Image.new("RGB", (width, height), "BLACK")
draw = ImageDraw.Draw(image)
display.image(image)
blank_matrix = np.zeros((height, width, 3), dtype=np.uint8)

# --- Typography Setup (Using Monospaced Fonts) ---
try:
    font_meta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 13)
    font_tc = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 24)
    font_icon = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
except IOError:
    font_meta = font_tc = font_icon = ImageFont.load_default()



make_playlist()
if AUTO_START:
    player_mode = "play"  # autoplay
    GPIO.output(12, GPIO.HIGH)

# --- Main Render Loop ---
try:
    while True:
        # 1. Math for Timecode (HH:MM:SS:FF)
        total_seconds = latest_time_pos
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        fractional_seconds = total_seconds - int(total_seconds)
        frames = int(fractional_seconds * fps)

        # 2. Format UI Strings
        playlist_str = f"CLIP {playlist_pos:02d}/{playlist_count:02d}"
        #timecode_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
        timecode_str = f"{minutes:02d}:{seconds:02d}:{frames:02d}"
        status_icon = "||" if is_paused else "> "  # Clean monospaced layout icons

        # 3. Clear canvas array instantly with NumPy
        np_frame = np.array(image)
        np_frame[:, :] = blank_matrix
        image = Image.fromarray(np_frame)
        draw = ImageDraw.Draw(image)

        # 4. Draw UI Layout Elements
        # Top Metadata Layer (Clip position + Status Icon)
        draw.text((8, 15), playlist_str, font=font_meta, fill=(255, 128, 0)) # Dim Orange 200,100,0
        icon_color = (255, 128, 0) if is_paused else (255, 128, 0)  # 255,0,0 else 0,255,0
        draw.text((105, 13), status_icon, font=font_icon, fill=icon_color)

        # Center Timecode Layer
        draw.text((4, 52), timecode_str, font=font_tc, fill=(255, 128, 0))   # Cyan 0,255,255

        # Bottom Progress Bar Layer
        bar_x1, bar_y1 = 8, 95
        bar_x2, bar_y2 = width - 8, 101
        bar_width = bar_x2 - bar_x1

        # Draw empty background track rectangle
        draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill=(40, 40, 40))

        # Calculate progress fill width
        if duration > 0:
            progress_pct = min(max(total_seconds / duration, 0.0), 1.0)
            fill_x2 = bar_x1 + int(bar_width * progress_pct)
            if fill_x2 > bar_x1:
                # Draw filled active tracking rectangle over the base
                draw.rectangle([bar_x1, bar_y1, fill_x2, bar_y2], fill=(255, 128, 0))  # 0,255,255

        # 5. Push final layout matrix block to display hardware
        display.image(image)

        # ~30 updates per second
        time.sleep(0.033)

except KeyboardInterrupt:
    player.terminate()
    display.image(Image.new("RGB", (width, height), "BLACK"))
