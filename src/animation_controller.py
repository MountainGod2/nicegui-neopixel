import asyncio

import board
import neopixel
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.color import BLACK, RED
from adafruit_led_animation.sequence import AnimationSequence
from nicegui import app, ui

num_pixels = 100
pixel_pin = board.D18


class AnimationController:
    def __init__(self):
        self.comet_speed = 0.01
        self.comet_color = RED
        self.comet_bounce = True
        self.comet_background_color = BLACK
        self.comet_tail_length = 10
        self.pulse_speed = 0.01
        self.pulse_color = RED
        self.pulse_period = 2
        self.running = False
        self.strip_pixels = None

    def create_pixels(self):
        self.strip_pixels = neopixel.NeoPixel(
            pin=pixel_pin, n=num_pixels, brightness=0.1, auto_write=False
        )
        return self.strip_pixels

    def create_animations(self, strip_pixels):
        comet_animation = Comet(
            pixel_object=strip_pixels,
            speed=self.comet_speed,
            color=self.comet_color,
            bounce=self.comet_bounce,
            background_color=self.comet_background_color,
            tail_length=self.comet_tail_length,
            name="Comet",
        )

        pulse_animation = Pulse(
            pixel_object=strip_pixels,
            speed=self.pulse_speed,
            color=self.pulse_color,
            period=self.pulse_period,
            name="Pulse",
        )

        self.animation_sequence = AnimationSequence(
            comet_animation,
            pulse_animation,
            advance_interval=None,
            auto_clear=True,
        )
        return self.animation_sequence

    def clear_pixels(self, strip_pixels):
        strip_pixels.fill((0, 0, 0))
        strip_pixels.show()

    def start_animations(self):
        if not self.running:
            self.running = True
            asyncio.create_task(self.run_animation_sequence())

    async def stop_animations(self):
        self.running = False
        self.clear_pixels(self.strip_pixels)

    async def run_animation_sequence(self):
        while self.running:
            self.animation_sequence.animate()
            await asyncio.sleep(0)

    def current_animation(self):
        app.storage.general.update(
            {"current_animation": self.animation_sequence.current_animation.name}
        )
        print(self.animation_sequence.current_animation.name)


def update_comet_speed(value):
    # Ensure that the function receives a numeric value for speed
    animation_controller.comet_speed = float(value)
    # Re-initialize animations to apply changes
    animation_controller.create_animations(pixels)


def update_comet_tail_length(value):
    # Ensure that the function receives a numeric value for speed
    animation_controller.comet_tail_length = int(value)
    # Re-initialize animations to apply changes
    animation_controller.create_animations(pixels)


def update_comet_bounce(value):
    animation_controller.comet_bounce = bool(value)
    # Re-initialize animations to apply changes
    animation_controller.create_animations(pixels)


def update_comet_color(value):
    # Extract the numeric parts from the string 'rgb(0,0,0)' and convert them to integers
    rgb_values = value.strip("rgb()").split(",")
    rgb_tuple = tuple(int(val.strip()) for val in rgb_values)

    # Update the comet color with the new RGB tuple
    animation_controller.comet_color = rgb_tuple
    # Re-initialize animations to apply changes
    animation_controller.create_animations(pixels)


def update_comet_background_color(value):
    # Extract the numeric parts from the string 'rgb(0,0,0)' and convert them to integers
    rgb_values = value.strip("rgb()").split(",")
    rgb_tuple = tuple(int(val.strip()) for val in rgb_values)

    # Update the comet color with the new RGB tuple
    animation_controller.comet_background_color = rgb_tuple
    # Re-initialize animations to apply changes
    animation_controller.create_animations(pixels)


def update_pulse_speed(value):
    animation_controller.pulse_speed = value
    # Re-initialize animations to apply changes
    animation_controller.create_animations(pixels)


def update_pulse_period(value):
    # Ensure that the function receives a numeric value for speed
    pulse_period_value = int(value)
    animation_controller.pulse_period = pulse_period_value
    # Re-initialize animations to apply changes
    animation_controller.create_animations(pixels)


def update_pulse_color(value):
    # Extract the numeric parts from the string 'rgb(0,0,0)' and convert them to integers
    rgb_values = value.strip("rgb()").split(",")
    rgb_tuple = tuple(int(val.strip()) for val in rgb_values)

    # Update the pulse color with the new RGB tuple
    animation_controller.pulse_color = rgb_tuple
    # Re-initialize animations to apply changes
    animation_controller.create_animations(pixels)


def toggle_animation():
    if animation_controller.running:
        asyncio.create_task(animation_controller.stop_animations())
    else:
        animation_controller.start_animations()


def next_animation():
    animation_controller.animation_sequence.next()
    animation_controller.current_animation()
    animation_controller.animation_sequence.animate()


def previous_animation():
    animation_controller.animation_sequence.previous()
    animation_controller.current_animation()
    animation_controller.animation_sequence.animate()


animation_controller = AnimationController()
pixels = animation_controller.create_pixels()
animations = animation_controller.create_animations(pixels)
storage = app.storage.general


# Initialize the UI
@ui.page("/")
def index():
    storage.setdefault("current_animation", "")
    animation_controller.current_animation()
    with ui.card().classes("mx-auto").style(add="max-width: 500px; height: 700px;"):
        # Create a label with a large font size and bold text
        ui.label("Animation Control Panel").style(
            add="font-size: 1.5rem; font-weight: bold;"
        ).classes("mx-auto")
        with ui.row().classes("mx-auto"):
            with ui.card().bind_visibility_from(
                storage, "current_animation", lambda value: value == "Comet"
            ):
                with ui.column():
                    ui.label("Comet Settings").style(
                        add="font-size: 1rem; font-weight: bold;"
                    )
                    ui.label("Speed")
                    ui.slider(
                        value=animation_controller.comet_speed,
                        min=0.001,
                        max=0.1,
                        step=0.001,
                        on_change=lambda event: update_comet_speed(event.value),
                    )
                    ui.label("Tail Length")
                    ui.slider(
                        value=animation_controller.comet_tail_length,
                        min=1,
                        max=num_pixels,
                        step=1,
                        on_change=lambda event: update_comet_tail_length(event.value),
                    )
                    ui.label("Bounce")
                    ui.checkbox(
                        value=animation_controller.comet_bounce,
                        on_change=lambda event: update_comet_bounce(event.value),
                    )
                    ui.label("Color")
                    ui.color_input(
                        value=animation_controller.comet_color,
                        on_change=lambda event: update_comet_color(event.value),
                    )

            with ui.card().bind_visibility_from(
                storage, "current_animation", lambda value: value == "Pulse"
            ):
                with ui.column():
                    ui.label("Pulse Settings").style(
                        add="font-size: 1rem; font-weight: bold;"
                    )
                    ui.label("Speed")
                    ui.slider(
                        value=animation_controller.pulse_speed,
                        min=0.01,
                        max=0.1,
                        step=0.01,
                        on_change=lambda event: update_pulse_speed(event.value),
                    )
                    ui.label("Period")
                    ui.slider(
                        value=animation_controller.pulse_period,
                        min=1,
                        max=10,
                        step=1,
                        on_change=lambda event: update_pulse_period(event.value),
                    )
                    ui.label("Color")
                    ui.color_input(
                        value=animation_controller.pulse_color,
                        on_change=lambda event: update_pulse_color(event.value),
                    )

        with ui.row().classes("mx-auto"):
            ui.button(on_click=previous_animation, icon="arrow_back").classes("mx-auto")
            ui.button("Start/Stop Animation", on_click=toggle_animation).classes(
                "mx-auto"
            )
            ui.button(on_click=next_animation, icon="arrow_forward").classes("mx-auto")


# Start the NiceGUI event loop
ui.run(title="NiceGUI Animation Controller")
