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

# Initialize NeoPixel strip
pixels = neopixel.NeoPixel(
    board.D18, PIXEL_COUNT, brightness=BRIGHTNESS, auto_write=False
)

# Initialize storage
storage = app.storage.general

# Set default animation parameters
animation_params = {
    "blink": {
        "speed": 1,
        "color": "(255,0,153)",
        "name": "blink",
    },
    "comet": {
        "speed": 0.1,
        "color": "(255,0,153)",
        "background_color": "(0,0,0)",
        "tail_length": 10,
        "bounce": True,
        "reverse": False,
        "name": "comet",
    },
    "rainbow": {
        "speed": 0.1,
        "period": 10,
        "step": 1,
        "precompute_rainbow": True,
        "name": "rainbow",
    },
}

# Set default animation and control variables
storage.setdefault("animation_running", False)
storage.setdefault("stop_requested", False)


# Function to create an animation based on the selected value
async def start_animation(animation_select):
    selected_animation = animation_select.value
    storage["stop_requested"] = False
    await create_animation(selected_animation)


async def create_animation(selected_animation):
    animation_params[selected_animation]["name"] = selected_animation
    animation = None

    if selected_animation == "blink":
        animation = Blink(pixels, **animation_params[selected_animation])
    elif selected_animation == "comet":
        params = animation_params[selected_animation]
        params["color"] = tuple(int(x) for x in params["color"].strip("()").split(","))
        params["background_color"] = tuple(
            int(x) for x in params["background_color"].strip("()").split(",")
        )
        animation = Comet(pixels, **params)
    elif selected_animation == "rainbow":
        animation = Rainbow(pixels, **animation_params[selected_animation])

    if animation:
        await run_animation(animation)


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
        ui.label(label_text).style("color: #666666; font-size: 0.7rem").classes("my-3")
        ui.label().bind_text_from(param, label_text.lower()).style(
            "color: #666666; font-size: 0.7rem"
        ).classes("my-3")


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
    with ui.card().classes("mx-auto").style("width: 400px; padding: 20px") as container:
        ui.label("LED Animation").classes("mx-auto").style(
            "font-size: 1.5rem; font-weight: bold;"
        ).tailwind("text-sky-500 dark:text-sky-400")

        with ui.row():
            ui.label("Select Animation:").style("font-weight: bold;").classes(
                "mx-auto my-auto"
            ).tailwind("text-sky-500 dark:text-sky-400")
            animation_select = ui.select(["blink", "comet", "rainbow"], value="comet")

        animation_params_ui = {
            "blink": create_params_ui(
                animation_params["blink"], animation_select, "blink"
            ),
            "comet": create_params_ui(
                animation_params["comet"], animation_select, "comet"
            ),
            "rainbow": create_params_ui(
                animation_params["rainbow"], animation_select, "rainbow"
            ),
        }

        with ui.row().classes("mx-auto"):
            ui.button("Stop", on_click=stop_animation).classes(
                "mx-auto my-4 bg-red-500 hover:bg-red-400 text-white font-bold py-2 px-4 rounded"
            )
            ui.button(
                "Start", on_click=lambda: start_animation(animation_select)
            ).classes(
                "mx-auto my-4 bg-sky-500 hover:bg-sky-400 text-white font-bold py-2 px-4 rounded"
            )

        # Create UI for the selected animation parameters
        selected_animation = animation_select.value
        selected_params_ui = animation_params_ui.get(selected_animation, None)
        if selected_params_ui:
            with selected_params_ui:
                pass


# Function to create UI elements for animation parameters
def create_params_ui(params, animation_select, animation_name):
    params_ui = (
        ui.element()
        .classes("w-full")
        .bind_visibility_from(animation_select, "value", value=animation_name)
    )

    with params_ui:
        apply_standard_style(params_ui, params, "Speed")
        apply_slider(params_ui, params, 0.01, 0.5, 0.01, "speed")
        apply_color_input(params_ui, params, "Color:", "color")

        if animation_name == "comet":
            apply_color_input(
                params_ui, params, "Background color:", "background_color"
            )
            apply_standard_style(params_ui, params, "Tail length")
            apply_slider(params_ui, params, 2, 100, 1, "tail_length")
            apply_checkbox(params_ui, params, "Bounce", "bounce")
            apply_checkbox(params_ui, params, "Reverse", "reverse")

        if animation_name == "rainbow":
            apply_standard_style(params_ui, params, "Period")
            apply_slider(params_ui, params, 1, 120, 1, "period")
            apply_standard_style(params_ui, params, "Step")
            apply_slider(params_ui, params, 1, 10, 1, "step")
            apply_checkbox(
                params_ui, params, "Precompute rainbow", "precompute_rainbow"
            )

    return params_ui


# Run the UI
ui.run()
