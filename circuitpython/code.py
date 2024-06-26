# Import required libraries
import rotaryio
import keypad
import board
import displayio
import terminalio
import busio
import usb_hid  # Add this import
from adafruit_display_text import label
import adafruit_displayio_ssd1306
from adafruit_hid.keycode import Keycode as K
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

displayio.release_displays()
oled_reset = board.D4  #this doesn't actually do anything right now but is required
i2c = busio.I2C(board.D3, board.D2)  
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=oled_reset)

WIDTH = 128
HEIGHT = 32
BORDER = 5

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)
# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
splash.append(inner_sprite)

# Draw a label
text = "CircuitPython"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2 - 1
)
splash.append(text_area)

def setup_keypad():
    # Initialize keypad and return the objects
    keys = keypad.KeyMatrix(
        row_pins=(board.CLK, board.MISO, board.MOSI, board.D10, board.D5),
        column_pins=(board.A0, board.A1, board.A2, board.A3),
        columns_to_anodes=False,
    )
    keycodes = [K.A, K.B, K.C, K.D, K.E, K.F, K.G, K.H, K.I, K.J, K.K, K.L, K.M, K.N, K.O, K.P, K.Q]
    return keys, keycodes

def setup_hid_devices():
    # Initialize HID devices and return the objects
    kbd = Keyboard(usb_hid.devices)
    cc = ConsumerControl(usb_hid.devices)
    return kbd, cc

def setup_rotary_encoder():
    # Initialize rotary encoder and return the object
    return rotaryio.IncrementalEncoder(board.D9, board.D8)

def process_rotary_encoder(encoder, cc, text_area, last_position=0, display=None):
    # Process the rotation of the encoder
    if last_position is None:
        last_position = 0
    position = encoder.position
    if last_position != position:
        position_change = position - last_position
        for _ in range(abs(position_change)):
            action = ConsumerControlCode.VOLUME_INCREMENT if position_change > 0 else ConsumerControlCode.VOLUME_DECREMENT
            cc.send(action)
        if position_change > 0:
            text_area.text = "Volume +"
        else:
            text_area.text = "Volume -"
        last_position = position
        if display is not None:
            display.refresh()
    return last_position

def process_keypad_events(keys, keycodes, kbd, text_area, display):
    if ev := keys.events.get():
        keycode = keycodes[ev.key_number]
        if ev.pressed:
            kbd.press(keycode)
            text_area.text = str(ev.key_number) + " key press"
        else:
            kbd.release(keycode)
            text_area.text = ""  # Clear text when key is released
        display.refresh()

def main():
    keys, keycodes = setup_keypad()
    kbd, cc = setup_hid_devices()
    encoder = setup_rotary_encoder()

    last_position = None

    while True:
        last_position = process_rotary_encoder(encoder, cc, text_area, last_position, display=display)
        process_keypad_events(keys, keycodes, kbd, text_area, display=display)

if __name__ == "__main__":
    main()
