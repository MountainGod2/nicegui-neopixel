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

# Set default values for animations
blink_params = storage.setdefault(
    "blink_params",
    {
        "speed": 0.1,
        "color": "(255,0,153)",
        "name": "blink",
    },
)

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


storage.setdefault("animation_running", False)
storage.setdefault("stop_requested", False)


# Function to create an animation based on the selected value
async def start_animation(animation_select):
    selected_animation = animation_select.value
    storage["stop_requested"] = False
    if selected_animation == "blink":
        await blink_animation()
    elif selected_animation == "rainbow":
        await rainbow_animation()
    elif selected_animation == "comet":
        await comet_animation()


async def blink_animation():
    blink_params = storage.get("blink_params")
    speed = blink_params["speed"]
    color = tuple(map(int, blink_params["color"].strip("()").split(",")))
    name = blink_params["name"]

    blink = Blink(pixels, speed=speed, color=color, name=name)
    await run_animation(blink)


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


# Function to stop the animation
def stop_animation():
    storage["stop_requested"] = True


# Function to run an animation
async def run_animation(animation):
    if not storage.get("animation_running"):
        try:
            storage["animation_running"] = True
            while not storage["stop_requested"]:
                animation.animate()
                await asyncio.sleep(0)
        except (asyncio.CancelledError, KeyboardInterrupt, RuntimeError):
            pass
        finally:
            pixels.fill((0, 0, 0))
            pixels.show()
            storage["animation_running"] = False
            storage["stop_requested"] = False


# Reusable styling functions
def apply_standard_style(parent, param, label_text):
    with parent:
        ui.label(label_text).style("color: #666666; font-size: 0.8rem")
        ui.label().bind_text_from(param, label_text.lower()).style(
            "color: #666666; font-size: 0.8rem"
        )


def apply_slider(parent, param, min_val, max_val, step_val, param_name):
    with parent:
        return ui.slider(min=min_val, max=max_val, step=step_val).bind_value(
            param, param_name
        )


def apply_color_input(parent, param, label, param_name):
    with parent:
        return ui.color_input(label=label).bind_value(
            param,
            param_name,
            backward=lambda x: f"rgb{x}",
            forward=lambda x: x.replace("rgb", ""),
        )


def apply_checkbox(parent, param, label, param_name):
    with parent:
        ui.label(label).classes("my-auto")
        return ui.checkbox().bind_value(param, param_name)


# Create UI
@ui.page(path="/")
def index():
    with ui.card().classes("mx-auto").style("width: 300px") as container:
        with ui.row():
            ui.label("Animation:").style("font-weight: bold;").classes(
                "mx-auto; my-auto"
            ).tailwind("text-sky-500 dark:text-sky-400")
            animation_select = ui.select(["blink", "comet", "rainbow"], value="comet")

        blink_params_ui = (
            ui.element()
            .classes("w-full")
            .bind_visibility_from(animation_select, "value", value="blink")
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

        # Blink Parameters UI
        with blink_params_ui:
            apply_standard_style(blink_params_ui, blink_params, "Speed")
            apply_slider(blink_params_ui, blink_params, 0.01, 1, 0.01, "speed")
            apply_color_input(blink_params_ui, blink_params, "Color:", "color")

        with ui.element().classes("mx-auto") as button_container:
            with ui.row():
                ui.button("Stop", on_click=stop_animation).classes("mx-auto")
                ui.button(
                    "Start", on_click=lambda: start_animation(animation_select)
                ).classes("mx-auto")

        # Comet Parameters UI
        with comet_params_ui:
            apply_standard_style(comet_params_ui, comet_params, "Speed")
            apply_slider(comet_params_ui, comet_params, 0.01, 1, 0.01, "speed")
            apply_color_input(comet_params_ui, comet_params, "Color:", "color")
            apply_color_input(
                comet_params_ui, comet_params, "Background color:", "background_color"
            )
            apply_standard_style(comet_params_ui, comet_params, "Tail length")
            apply_slider(comet_params_ui, comet_params, 2, 100, 1, "tail_length")
            apply_checkbox(comet_params_ui, comet_params, "Bounce", "bounce")
            apply_checkbox(comet_params_ui, comet_params, "Reverse", "reverse")

        # Rainbow Parameters UI
        with rainbow_params_ui:
            apply_standard_style(rainbow_params_ui, rainbow_params, "Speed")
            apply_slider(rainbow_params_ui, rainbow_params, 0.01, 1, 0.01, "speed")
            apply_standard_style(rainbow_params_ui, rainbow_params, "Period")
            apply_slider(rainbow_params_ui, rainbow_params, 1, 120, 1, "period")
            apply_standard_style(rainbow_params_ui, rainbow_params, "Step")
            apply_slider(rainbow_params_ui, rainbow_params, 1, 10, 1, "step")
            apply_checkbox(
                rainbow_params_ui,
                rainbow_params,
                "Precompute rainbow",
                "precompute_rainbow",
            )


# Run the UI
ui.run()
