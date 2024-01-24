import asyncio
import board
import neopixel
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.color import AMBER, JADE, PURPLE

from nicegui import ui, app


class AnimationController:
    def __init__(self, storage):
        self.storage = storage
        self.pixels = neopixel.NeoPixel(
            board.D18, 100, brightness=0.2, auto_write=False
        )
        self.animation_objects = self.configure_animations()
        self.animation_sequence = None
        self.animation_task = None

    def configure_animations(self):
        # Create a dictionary of animation objects
        return {
            "blink": Blink(self.pixels, speed=0.5, color=(255, 0, 0)),
            "comet": Comet(self.pixels, speed=0.05, color=(0, 255, 0), tail_length=10),
            "chase": Chase(
                self.pixels, speed=0.1, color=(0, 0, 255), size=6, spacing=5
            ),
            "pulse": Pulse(self.pixels, speed=0.1, period=3, color=AMBER),
            "sparkle": Sparkle(self.pixels, speed=0.1, color=PURPLE, num_sparkles=10),
            "solid": Solid(self.pixels, color=JADE),
            "rainbow": Rainbow(self.pixels, speed=0.1, period=2),
            "sparkle_pulse": SparklePulse(self.pixels, speed=0.1, period=3, color=JADE),
            "rainbow_comet": RainbowComet(
                self.pixels, speed=0.1, tail_length=20, bounce=True
            ),
            "rainbow_chase": RainbowChase(
                self.pixels,
                speed=0.1,
                size=3,
                spacing=2,
                step=8,
            ),
            "rainbow_sparkle": RainbowSparkle(
                self.pixels,
                speed=0.1,
                num_sparkles=15,
            ),
        }

    def create_animation_sequence(self, selected_animations):
        selected_animation_objects = [
            self.animation_objects[anim] for anim in selected_animations
        ]
        return AnimationSequence(
            *selected_animation_objects,
            advance_interval=None,
            auto_clear=True,
            auto_reset=True,
        )

    async def start_animations(self):
        if self.animation_task is None or self.animation_task.done():
            selected_animations = self.storage.get("animation_selection")
            self.animation_sequence = self.create_animation_sequence(
                selected_animations
            )
            self.storage.update({"animation_running": True})
            self.animation_task = asyncio.create_task(self.animate_loop())

    async def animate_loop(self):
        while True:
            self.animation_sequence.animate()
            await asyncio.sleep(0.01)

    def stop_animations(self):
        if self.animation_task and not self.animation_task.done():
            if self.storage.get("animation_frozen", True):
                self.animation_sequence.resume()
            self.animation_task.cancel()
            self.animation_task = None
            self.reset_animation_state()

    def reset_animation_state(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        self.animation_sequence = None
        self.storage.update({"animation_running": False, "animation_frozen": False})

    def next_animation(self):
        if self.animation_sequence:
            if self.storage.get("animation_frozen", True):
                self.animation_sequence.resume()
            self.animation_sequence.next()

    def previous_animation(self):
        if self.animation_sequence:
            if self.storage.get("animation_frozen", True):
                self.animation_sequence.resume()
            self.animation_sequence.previous()

    def toggle_animation_freeze(self):
        frozen = not self.storage.get("animation_frozen", False)
        self.storage["animation_frozen"] = frozen  # Update the storage directly
        if self.animation_sequence:
            if not frozen:
                self.animation_sequence.resume()
            else:
                self.animation_sequence.freeze()
        ui.update()


@ui.page("/")
def index():
    ui.colors(
        primary="#ff94b6", secondary="#fff4f7", positive="#bcc2e7", negative="#e7bcc2"
    )
    storage = app.storage.general
    controller = AnimationController(storage)
    storage.setdefault("animation_selection", [])
    storage.update({"animation_running": False, "animation_frozen": False})
    with ui.element().style(
        "border: 4px solid #ff94b6; border-radius: 15px; background-color: #fff4f7; margin: 20px auto; max-width: 500px;"
    ):
        with ui.column().classes("p-4"):
            with ui.row().classes("justify-center mb-4"):  # Centered horizontally
                available_animations = list(controller.animation_objects.keys())
                animation_selection = (
                    ui.select(
                        available_animations,
                        multiple=True,
                        label="Available Animations:",
                    )
                    .classes("w-64")
                    .props("use-chips")
                ).bind_value_to(storage, "animation_selection")

            with ui.row().classes("justify-center mx-auto"):  # Centered horizontally
                start_button = (
                    ui.button(
                        "Start", on_click=controller.start_animations, color="positive"
                    )
                    .bind_visibility_from(
                        storage, "animation_running", backward=lambda x: not x
                    )
                    .style("align-self: center; border-radius: 15px;")
                )
                stop_button = (
                    ui.button(
                        "Stop", on_click=controller.stop_animations, color="negative"
                    )
                    .bind_visibility_from(storage, "animation_running")
                    .style("align-self: center; border-radius: 15px;")
                )

            with ui.element().classes("p-4 mx-auto").bind_visibility_from(
                storage, "animation_running"
            ):
                with ui.row().classes(
                    "justify-center mb-4 mx-auto"
                ):  # Centered horizontally and added margin-bottom
                    previous_button = ui.button(
                        "Previous",
                        on_click=controller.previous_animation,
                        color="primary",
                    ).style("align-self: center; border-radius: 15px;")
                    advance_button = ui.button(
                        "Advance",
                        on_click=controller.next_animation,
                        color="primary",
                    ).style("align-self: center; border-radius: 15px;")
                with ui.row().classes(
                    "justify-center mx-auto"
                ):  # Centered horizontally
                    freeze_switch = ui.switch(
                        text="Freeze Animation",
                        on_change=controller.toggle_animation_freeze,
                    ).bind_value_to(
                        storage, "animation_frozen", forward=lambda x: not x
                    )


ui.run()
