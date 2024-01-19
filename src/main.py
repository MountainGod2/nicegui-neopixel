import asyncio
import board
import neopixel
from nicegui import ui
import webcolors

# Check the available digital pins from the adafruit board module
pins = [pin for pin in dir(board) if pin.startswith("D")]


class LEDStrip:
    def __init__(self, pin: str, num_leds: int, brightness: float):
        self.pin = pin
        self.num_leds = num_leds
        self.brightness = brightness
        self.led_strip = neopixel.NeoPixel(
            getattr(board, self.pin),
            n=self.num_leds,
            brightness=self.brightness,
            auto_write=False,
        )

    def update_led_strip(self, color: str, pin: str, num_leds: int, brightness: float):
        color = webcolors.hex_to_rgb(color)
        if (
            self.pin != pin
            or self.num_leds != num_leds
            or self.brightness != brightness
        ):
            self.pin = pin
            self.num_leds = num_leds
            self.brightness = brightness
            self.led_strip = neopixel.NeoPixel(
                getattr(board, self.pin), self.num_leds, brightness=self.brightness
            )
        self.led_strip.fill(color)
        self.led_strip.show()

    def turn_off(self):
        color = webcolors.name_to_rgb("black")
        self.led_strip.fill(color)
        self.color_picker.value = webcolors.rgb_to_hex(color)

    async def handle_update(self):
        color = self.color_picker.value
        pin = self.pin_dropdown.value
        num_leds = int(self.num_leds_input.value)
        brightness = self.brightness_slider.value
        self.update_led_strip(color, pin, num_leds, brightness)
        await asyncio.sleep(0)


@ui.page("/")
async def index():
    with ui.card():
        led_strip_control = LEDStrip(pin="D18", num_leds=30, brightness=0.1)
        with ui.column():
            pin_dropdown_label = ui.label(text="Select a pin:")
            led_strip_control.pin_dropdown = ui.select(
                value="D18",
                options=pins,
                on_change=led_strip_control.handle_update,
            )
            ui.separator()

            num_leds_label = ui.label(text="Number of LEDs:")
            led_strip_control.num_leds_input = ui.number(
                value=1,
                min=1,
                on_change=led_strip_control.handle_update,
            )
            ui.separator()

            color_picker_label = ui.label(text="Select a color:")
            led_strip_control.color_picker = ui.color_input(
                value="#ff0000",
                on_change=led_strip_control.handle_update,
            )
            ui.separator()

            brightness_slider_label = ui.label(text="Adjust brightness:")
            led_strip_control.brightness_slider = ui.slider(
                value=0.1,
                min=0.1,
                max=0.4,  # Limited due to LED brightness, can be increased if needed (up to 1.0)
                step=0.01,
                on_change=led_strip_control.handle_update,
            )
            ui.separator()

            off_button = ui.button(text="Turn Off", on_click=led_strip_control.turn_off)


ui.run(title="LED Strip Control")
