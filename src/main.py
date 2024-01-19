# Import necessary libraries
import asyncio
import board
import neopixel
from nicegui import ui
import webcolors


# Check the available digital pins from the adafruit board module
pins = [pin for pin in dir(board) if pin.startswith("D")]


# Class for controlling the LED strip
class LEDStrip:
    def __init__(self, pin: str, num_leds: int, brightness: float):
        # Initialize the LEDStrip object with the given parameters
        self.pin = pin
        self.num_leds = num_leds
        self.brightness = brightness
        # Create a NeoPixel object to control the LED strip
        self.led_strip = neopixel.NeoPixel(
            pin=getattr(board, self.pin),
            n=self.num_leds,
            brightness=self.brightness,
            auto_write=False,
        )

    # Function to update the LED strip with new settings
    def update_led_strip(self, color: str, pin: str, num_leds: int, brightness: float):
        # Convert the color from a hex string to an RGB tuple using webcolors
        color = webcolors.hex_to_rgb(color)

        # Check if the pin or number of LEDs has changed
        if (
            self.pin != pin
            or self.num_leds != num_leds
            or self.brightness != brightness
        ):
            # Update the pin, number of LEDs, and brightness
            self.pin = pin
            self.num_leds = num_leds
            self.brightness = brightness

            # Create a new NeoPixel object with the updated pin and num_leds
            self.led_strip = neopixel.NeoPixel(
                getattr(board, self.pin), self.num_leds, brightness=self.brightness
            )

        # Fill the LED strip with the new color and show the changes
        self.led_strip.fill(color)
        self.led_strip.show()

    # Function to turn off the LED strip
    def turn_off(self):
        # Use webcolors to get the RGB value for the color black
        color = webcolors.name_to_rgb("black")
        # Fill the LED strip with the black color to turn it off
        self.led_strip.fill(color)
        # Update the color picker in the UI to reflect the new color (black)
        self.color_picker.value = webcolors.rgb_to_hex(color)

    # Asynchronous function to handle updates from the UI elements
    async def handle_update(self):
        # Get the current values from the UI elements
        color = self.color_picker.value
        pin = self.pin_dropdown.value
        num_leds = int(self.num_leds_input.value)
        brightness = self.brightness_slider.value
        # Call the update_led_strip method with the new settings
        self.update_led_strip(color, pin, num_leds, brightness)
        await asyncio.sleep(0)


# Create the user interface (UI) elements using the nicegui library
with ui.card():
    # Create an instance of the LEDStrip class with initial pin and num_leds values
    led_strip_control = LEDStrip(pin="D18", num_leds=30, brightness=0.1)

    with ui.column():
        # Dropdown to select the pin
        led_strip_control.pin_dropdown = ui.select(
            value="D18", options=pins, on_change=led_strip_control.handle_update
        )
        # Input field to set the number of LEDs
        led_strip_control.num_leds_input = ui.number(
            label="Number of LEDs",
            value=1,
            min=1,
            on_change=led_strip_control.handle_update,
        )
        # Color picker to select the LED strip color
        led_strip_control.color_picker = ui.color_input(
            value="#ff0000", on_change=led_strip_control.handle_update
        )
        # Slider to adjust the brightness (0.1 to 1.0)
        led_strip_control.brightness_slider = ui.slider(
            value=0.1,
            min=0.1,
            max=1.0,
            step=0.01,
            on_change=led_strip_control.handle_update,
        )
        # Button to turn off the LED strip
        off_button = ui.button(text="Turn Off", on_click=led_strip_control.turn_off)

# Run the UI with the specified title
ui.run(title="LED Strip Control")
