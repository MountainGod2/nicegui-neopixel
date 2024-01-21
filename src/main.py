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
        self.init_led_strip()
        self.primary_color = "#ff94b6"  # Initialize primary color
        self.secondary_color = self.calculate_secondary_color(self.primary_color)

        self.element = ui.element()

        with self.element.style(
            f"border: 4px solid {self.secondary_color}; border-radius: 15px;"
        ):
            with ui.card().classes("no-shadow border-[0px]").style(
                "border-radius: 15px;"
            ):
                ui.label.default_style(
                    add=f"color: {self.primary_color}; font-weight: bold;"
                )

                with ui.column():
                    pin_dropdown_label = ui.label(text="Select a pin:").classes(
                        replace="text-secondary"
                    )
                    self.pin_dropdown = ui.select(
                        value="D18",
                        options=pins,
                        on_change=self.handle_update,
                    )
                    ui.separator()

                    num_leds_label = ui.label(text="Number of LEDs:").classes(
                        replace="text-secondary"
                    )
                    self.num_leds_input = ui.number(
                        value=1,
                        min=1,
                        on_change=self.handle_update,
                    )
                    ui.separator()

                    color_picker_label = ui.label(text="Select a color:").classes(
                        replace="text-secondary"
                    )
                    self.color_picker = ui.color_input(
                        value=self.primary_color,
                        on_change=self.handle_update,
                    )
                    ui.separator()

                    brightness_slider_label = ui.label(
                        text="Adjust brightness:"
                    ).classes(replace="text-secondary")
                    self.brightness_slider = ui.slider(
                        value=0.1,
                        min=0.1,
                        max=0.4,
                        step=0.01,
                        on_change=self.handle_update,
                    )
                    ui.separator()

                    ui.button(
                        text="Turn Off",
                        on_click=self.turn_off,
                        color="primary",
                    ).style("align-self: center; border-radius: 15px;")

    def init_led_strip(self):
        self.led_strip = neopixel.NeoPixel(
            getattr(board, self.pin),
            n=self.num_leds,
            brightness=self.brightness,
            auto_write=False,
        )

    def calculate_secondary_color(self, primary: str):
        primary_tuple = webcolors.hex_to_rgb(primary)
        secondary_tuple = tuple(255 - val for val in primary_tuple)
        secondary_tuple = tuple(max(0, min(255, val)) for val in secondary_tuple)
        secondary = webcolors.rgb_to_hex(secondary_tuple)
        return secondary

    def update_border_color(self, primary: str):
        self.primary_color = primary
        border_color = f"border: 4px solid {primary}; border-radius: 15px;"
        self.element.style(border_color)

    def update_led_strip(self, color: str):
        color = webcolors.hex_to_rgb(color)
        self.led_strip.fill(color)
        self.led_strip.show()

    def turn_off(self):
        self.update_led_strip("#000000")
        self.color_picker.value = "#000000"

    def update_ui(self):
        ui.colors(
            primary=self.primary_color,
            secondary=self.secondary_color,
        )

    async def handle_update(self):
        color = self.color_picker.value
        pin = self.pin_dropdown.value
        num_leds = int(self.num_leds_input.value)
        brightness = self.brightness_slider.value
        primary = self.color_picker.value

        if primary != self.primary_color:
            self.primary_color = primary
            self.secondary_color = self.calculate_secondary_color(primary)
            self.update_border_color(self.primary_color)
            self.update_ui()

        if (
            pin != self.pin
            or num_leds != self.num_leds
            or brightness != self.brightness
        ):
            self.led_strip.deinit()
            self.led_strip = neopixel.NeoPixel(
                pin=getattr(board, pin),
                n=num_leds,
                brightness=brightness,
                auto_write=False,
            )

        self.update_led_strip(color)


@ui.page("/")
async def index():
    led_strip_control = LEDStrip(pin="D18", num_leds=30, brightness=0.1)


ui.run(title="LED Strip Control")
