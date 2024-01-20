import board
import neopixel
from nicegui import ui
import webcolors

# Define the available digital pins from the adafruit board module
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


@ui.page("/")
async def index():
    # Initialize with a default theme color
    initial_color = "#ff94b6"
    ui.colors(primary=initial_color, secondary="#f8b5c0")
    ui.label.default_style(add=f"color: {initial_color}; font-weight: bold;")

    led_strip_control = LEDStrip(pin="D18", num_leds=30, brightness=0.1)
    with ui.element().style(
        f"background-color: {initial_color}; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);border:3px solid #f8b5c0; border-radius: 15px; "
    ):
        with ui.card().style("border-radius: 15px;").classes("no-shadow border-[1px]"):
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
                    value=initial_color,
                    on_change=led_strip_control.handle_update,
                )
                ui.separator()

                brightness_slider_label = ui.label(text="Adjust brightness:")
                led_strip_control.brightness_slider = ui.slider(
                    value=0.1,
                    min=0.1,
                    max=0.4,
                    step=0.01,
                    on_change=led_strip_control.handle_update,
                )
                ui.separator()

                ui.button(
                    text="Turn Off",
                    on_click=led_strip_control.turn_off,
                    color="primary",
                ).style("align-self: center; border-radius: 15px;")


ui.run(title="LED Strip Control")
