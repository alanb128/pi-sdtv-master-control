import time
import rtc
import board
import keypad
import digitalio
from tm1637_display import TM1637Display

# Adjust pins based on your wiring
CLK_PIN = board.GP1
DIO_PIN = board.GP0

# Pins definition
BUTTON_PINS = (board.GP4, board.GP5, board.GP7, board.GP26)
buttons = keypad.Keys(BUTTON_PINS, value_when_pressed=False, pull=True)

# Initialize 6-digit display
display = TM1637Display(CLK_PIN, DIO_PIN, length=6, digit_order=[2,1,0,5,4,3])

display.brightness = 5 # Can be 0–7

# For setting the RTC
clocks = rtc.RTC()

# For the GPS button LED
gps_led = digitalio.DigitalInOut(board.GP27)
gps_led.direction = digitalio.Direction.OUTPUT
gps_led.value = False

# keep track of added hr/min
hour_add = 0
minute_add = 0

gps_enabled = False
set_state = False
show_dot = False

def time_set_display(hour, minute):
    # Updates the display during "set time" mode
    timestr = "{:02d}{:02d}{:02d}".format(hour, minute, 0)
    display.print(timestr)
    display.show_dots([False, True, False, True, False, False])

# Initialize timer for clock display update code
INTERVAL = 1.0
last_time = time.monotonic()

while True:

    # Read button clicks
    event = buttons.events.get()
    
    if event:
        if event.pressed:
            if event.key_number == 0:
                print("T button pressed.")
                if set_state:
                    # set new time
                    set_state = False
                    new_time = time.struct_time((2026, 6, 24, hour_add, minute_add, 0, 2, -1, -1))
                    clocks.datetime = new_time
                else:
                    # enter set mode
                    set_state = True
                    time_set_display(hour_add, minute_add)
            if event.key_number == 1:
                print("H button pressed.")
                if set_state:
                    hour_add = (hour_add + 1) % 24
                    time_set_display(hour_add, minute_add)
            if event.key_number == 2:
                print("M button pressed.")
                if set_state:
                    minute_add = (minute_add + 1) % 60
                    time_set_display(hour_add, minute_add)
            if event.key_number == 3:
                print("GPS button pressed.")
                gps_enabled = not gps_enabled
    
    # Check if one econd has passed:
    current_time = time.monotonic()
    if current_time - last_time >= INTERVAL:
        
        # All this code needs to happen once per second:
        
        now = time.localtime()

        hour = now.tm_hour 
        minute = now.tm_min
        second = now.tm_sec

        # Format as HHMMSS
        timestr = "{:02d}{:02d}{:02d}".format(hour, minute, second)
        print(timestr)
        if set_state:
            pass
        else:
            display.print(timestr)
            # Blink the colon (simulate separators)
            show_dot = not show_dot
            display.show_dots([False, show_dot, False, show_dot, False, False])
            
        if gps_enabled:
            gps_led.value = not gps_led.value
        else:
            gps_led.value = False
        
        # Reset the timer
        last_time = current_time
