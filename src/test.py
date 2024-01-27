import asyncio
import board
import neopixel
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.blink import Blink
from nicegui import app, ui

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
        "speed": 0.1,
        "color": "(255,0,153)",
        "background_color": "(0,0,0)",
        "tail_length": 10,
        "bounce": True,
        "reverse": False,
        "name": "comet",
    },
)

# Set default values for the Rainbow animation
rainbow_params = storage.setdefault(
    "rainbow_params",
    {
        "speed": 0.1,
        "period": 10,
        "step": 1,
        "precompute_rainbow": True,
        "name": "rainbow",
    },
)

# Set default values for the Blink animation
blink_params = storage.setdefault(
    "blink_params",
    {
        "speed": 0.1,
        "color": "(255,0,153)",
        "name": "blink",
    },
)
storage.setdefault("animation_running", False)
storage.setdefault("stop_requested", False)


# Function to create an animation based on the selected value
async def start_animation(animation_select):
    selected_animation = animation_select.value  # Get the selected animation
    storage["stop_requested"] = False  # Reset the stop flag here
    if selected_animation == "comet":
        await comet_animation()
    elif selected_animation == "rainbow":
        await rainbow_animation()
    elif selected_animation == "blink":
        await blink_animation()


# Function to create a Comet animation
async def comet_animation():
    comet_params = storage.get("comet_params")
    speed = comet_params["speed"]
    color = tuple(map(int, comet_params["color"].strip("()").split(",")))
    background_color = tuple(
        map(int, comet_params["background_color"].strip("()").split(","))
    )
    tail_length = comet_params["tail_length"]
    bounce = comet_params["bounce"]
    reverse = comet_params["reverse"]
    name = comet_params["name"]

    comet = Comet(
        pixels,
        speed=speed,
        color=color,
        background_color=background_color,
        tail_length=tail_length,
        bounce=bounce,
        reverse=reverse,
        name=name,
    )
    await run_animation(comet)


async def rainbow_animation():
    rainbow_params = storage.get("rainbow_params")
    speed = rainbow_params["speed"]
    period = rainbow_params["period"]
    step = rainbow_params["step"]
    precompute_rainbow = rainbow_params["precompute_rainbow"]
    name = rainbow_params["name"]

    rainbow = Rainbow(
        pixels,
        speed=speed,
        period=period,
        step=step,
        name=name,
        precompute_rainbow=precompute_rainbow,
    )
    await run_animation(rainbow)


async def blink_animation():
    blink_params = storage.get("blink_params")
    speed = blink_params["speed"]
    color = tuple(map(int, blink_params["color"].strip("()").split(",")))
    name = blink_params["name"]

    blink = Blink(pixels, speed=speed, color=color, name=name)
    await run_animation(blink)


# Function to stop the animation
def stop_animation():
    storage["stop_requested"] = True


# Function to run an animation
async def run_animation(animation):
    if not storage.get("animation_running"):
        try:
            storage["animation_running"] = True
            while not storage["stop_requested"]:  # Check the stop flag
                animation.animate()
                await asyncio.sleep(0)
        except (asyncio.CancelledError, KeyboardInterrupt, RuntimeError):
            pass
        finally:
            pixels.fill((0, 0, 0))
            pixels.show()
            storage["animation_running"] = False
            storage["stop_requested"] = False  # Reset the stop flag here


# Create UI
@ui.page(path="/")
def index():
    with ui.card().classes("mx-auto").style("width: 300px") as container:
        with ui.row():
            animation_label = (
                ui.label("Animation:")
                .style("font-weight: bold;")
                .classes("mx-auto; my-auto")
                .tailwind("text-sky-500 dark:text-sky-400")
            )

            animation_select = ui.select(
                ["comet", "rainbow", "blink"],
                value="comet",
            )
        comet_params_ui = (
            ui.element()
            .classes("w-full")
            .bind_visibility_from(animation_select, "value", value="comet")
        )
        rainbow_params_ui = (
            ui.element()
            .classes("w-full")
            .bind_visibility_from(animation_select, "value", value="rainbow")
        )
        blink_params_ui = (
            ui.element()
            .classes("w-full")
            .bind_visibility_from(animation_select, "value", value="blink")
        )

        with comet_params_ui:
            with ui.row():
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
                color_input = ui.color_input(label="Color:").bind_value(
                    comet_params,
                    "color",
                    backward=lambda x: f"rgb{x}",
                    forward=lambda x: x.replace("rgb", ""),
                )

            with ui.row().style("margin-top: 1.5rem"):
                background_color_input = ui.color_input(
                    label="Background color:"
                ).bind_value(
                    comet_params,
                    "background_color",
                    backward=lambda x: f"rgb{x}",
                    forward=lambda x: x.replace("rgb", ""),
                )

            with ui.row().style("margin-top: 1.5rem"):
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

            with ui.row():
                reverse_label = ui.label("Reverse:").classes("my-auto")
                reverse_checkbox = ui.checkbox().bind_value(comet_params, "reverse")

        with rainbow_params_ui:
            with ui.row():
                speed_label = ui.label("Speed:").style(
                    "color: #666666; font-size: 0.8rem"
                )
                speed_value = (
                    ui.label()
                    .bind_text_from(rainbow_params, "speed")
                    .style("color: #666666; font-size: 0.8rem")
                )

            speed_slider = ui.slider(min=0.01, max=1, step=0.01).bind_value(
                rainbow_params, "speed"
            )

            with ui.row():
                period_label = ui.label("Period:").style(
                    "color: #666666; font-size: 0.8rem"
                )
                period_value = (
                    ui.label()
                    .bind_text_from(rainbow_params, "period")
                    .style("color: #666666; font-size: 0.75rem")
                )

            period_slider = ui.slider(min=1, max=120, step=1).bind_value(
                rainbow_params, "period"
            )

            with ui.row():
                step_label = ui.label("Step:").style(
                    "color: #666666; font-size: 0.8rem"
                )
                step_value = (
                    ui.label()
                    .bind_text_from(rainbow_params, "step")
                    .style("color: #666666; font-size: 0.75rem")
                )

            step_slider = ui.slider(min=1, max=10, step=1).bind_value(
                rainbow_params, "step"
            )

            with ui.row():
                precompute_rainbow_label = ui.label("Precompute rainbow:").classes(
                    "my-auto"
                )
                precompute_rainbow_checkbox = ui.checkbox().bind_value(
                    rainbow_params, "precompute_rainbow"
                )

        with blink_params_ui:
            with ui.row():
                speed_label = ui.label("Speed:").style(
                    "color: #666666; font-size: 0.8rem"
                )
                speed_value = (
                    ui.label()
                    .bind_text_from(blink_params, "speed")
                    .style("color: #666666; font-size: 0.8rem")
                )

            speed_slider = ui.slider(min=0.01, max=1, step=0.01).bind_value(
                blink_params, "speed"
            )

            with ui.row():
                color_input = ui.color_input(label="Color:").bind_value(
                    blink_params,
                    "color",
                    backward=lambda x: f"rgb{x}",
                    forward=lambda x: x.replace("rgb", ""),
                )

        with ui.element().classes("mx-auto") as button_container:
            with ui.row():
                ui.button("Stop", on_click=stop_animation).classes("mx-auto")
                ui.button(
                    "Start", on_click=lambda: start_animation(animation_select)
                ).classes("mx-auto")


# Run the UI
ui.run()
