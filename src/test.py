import board
import neopixel
from adafruit_led_animation.animation.comet import Comet
from nicegui import ui, app
import asyncio

# Constants
PIXEL_COUNT = 100
BRIGHTNESS = 0.2

pixels = neopixel.NeoPixel(
    board.D18, PIXEL_COUNT, brightness=BRIGHTNESS, auto_write=False
)


# Initialize storage
storage = app.storage.general

# Set default values for the Comet animation
comet_params = storage.setdefault(
    "comet_params",
    {
        "color": "(0,229,255)",
        "speed": 0.1,
        "tail_length": 10,
        "bounce": True,
        "name": "comet",
    },
)

storage.setdefault("animation_running", False)


# Function to create a Comet animation
async def comet_animation():
    comet_params = storage.get("comet_params")
    color = tuple(map(int, comet_params["color"].strip("()").split(",")))
    speed = comet_params["speed"]
    tail_length = comet_params["tail_length"]
    bounce = comet_params["bounce"]
    name = comet_params["name"]

    comet = Comet(
        pixels,
        color=color,
        speed=speed,
        tail_length=tail_length,
        bounce=bounce,
        name=name,
    )
    await run_animation(comet)


# Function to run an animation
async def run_animation(animation):
    if not storage.get("animation_running"):
        try:
            storage["animation_running"] = True
            while True:
                animation.animate()
                await asyncio.sleep(0)
        except (asyncio.CancelledError, KeyboardInterrupt):
            storage["animation_running"] = False
        finally:
            pixels.fill((0, 0, 0))
            pixels.show()
            pixels.deinit()


# Create UI
@ui.page(path="/")
def index():
    with ui.card().classes("mx-auto").style("max-width: 500px") as root_container:
        with ui.row():
            animation_label = ui.label("Animation:").classes("my-auto")
            animation_select = ui.select(
                ["comet", "rainbow", "blink"],
                value="rainbow",
            )
        comet_params_ui = (
            ui.element()
            .classes("w-full")
            .bind_visibility_from(animation_select, "value", value="comet")
        )
        with comet_params_ui:
            with ui.row():
                comet_label = (
                    ui.label("Comet")
                    .style("font-weight: bold; font-size: 1.5rem")
                    .classes("mx-auto")
                    .tailwind("text-sky-500 dark:text-sky-400")
                )

            with ui.row().style("margin-top: 1rem"):
                color_input = ui.color_input(label="Color:").bind_value(
                    comet_params,
                    "color",
                    backward=lambda x: f"rgb{x}",
                    forward=lambda x: x.replace("rgb", ""),
                )

            with ui.row().style("margin-top: 1rem"):
                speed_label = ui.label("Speed:").style(
                    "color: #666666; font-size: 0.8rem"
                )
                speed_value = (
                    ui.label()
                    .bind_text_from(comet_params, "speed")
                    .style("color: #666666; font-size: 0.8rem")
                )

            speed_slider = ui.slider(min=0.01, max=1, step=0.01).bind_value(
                comet_params, "speed"
            )

            with ui.row():
                tail_length_label = ui.label("Tail length:").style(
                    "color: #666666; font-size: 0.8rem"
                )
                tail_length_value = (
                    ui.label()
                    .bind_text_from(comet_params, "tail_length")
                    .style("color: #666666; font-size: 0.75rem")
                )

            tail_length_slider = ui.slider(min=2, max=100, step=1).bind_value(
                comet_params, "tail_length"
            )

            with ui.row():
                bounce_label = ui.label("Bounce:").classes("my-auto")
                bounce_checkbox = ui.checkbox().bind_value(comet_params, "bounce")

            with ui.row().style("margin-top: 1rem"):
                ui.button("Start", on_click=comet_animation).classes("mx-auto")


# Run the UI
ui.run()
