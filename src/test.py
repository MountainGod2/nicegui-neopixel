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

# Initialize storage for app parameters
storage = app.storage.general

# Set default values for animation parameters
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

# Set default values for animation control flags
storage.setdefault("animation_running", False)
storage.setdefault("stop_requested", False)


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


def stop_animation():
    storage["stop_requested"] = True


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


def apply_standard_style(parent, param, label_text):
    with parent:
        label = ui.label(label_text).style("font-size: 0.8rem; color: #666;")
        return label


def apply_slider_with_label(
    parent, param, min_val, max_val, step_val, label_text, param_name
):
    with parent:
        label = apply_standard_style(parent, param, label_text)
        slider = ui.slider(min=min_val, max=max_val, step=step_val).bind_value(
            param, param_name
        )
        return label, slider


def apply_color_input(parent, param, label_text, param_name):
    with parent:
        color_input = (
            ui.color_input(label=label_text)
            .bind_value(
                param,
                param_name,
                backward=lambda x: f"rgb{x}",
                forward=lambda x: x.replace("rgb", ""),
            )
            .style("margin-bottom: 1.5rem; margin-top: -0.5rem;")
        )
        return color_input


def apply_checkbox_with_label(parent, param, label_text, param_name):
    with parent:
        label = ui.label(label_text).classes("my-auto").style("color: #666;")
        checkbox = ui.checkbox().bind_value(param, param_name)
        return label, checkbox


@ui.page(path="/")
def index():
    ui.colors(primary="#f48fb1")
    with ui.card().classes("mx-auto p-4 no-shadow border-[1px]").style(
        "border: 4px solid #f48fb1; border-radius: 15px; background-color: #fce4ec; margin: 20px auto; width: 80%; max-width: 500px; min-width: 300px"
    ) as container:
        ui.label("Animation Controller").classes(
            "mx-auto text-2xl font-bold text-pink-400 dark:text-pink-400"
        )

        with ui.row().classes("mx-auto"):
            ui.label("Select Animation:").classes(
                "my-auto text-pink-400 dark:text-pink-400"
            )
            # Animation type selection
            animation_select = ui.select(
                ["blink", "comet", "rainbow"], value="rainbow"
            ).classes("mx-auto")

        # Blink animation controls
        blink_controls = (
            ui.element()
            .bind_visibility_from(animation_select, "value", value="blink")
            .classes("w-full")
        )
        with blink_controls:
            apply_slider_with_label(
                blink_controls, blink_params, 0.01, 5, 0.1, "Speed:", "speed"
            )
            apply_color_input(blink_controls, blink_params, "Color:", "color")

        # Comet animation controls
        comet_controls = (
            ui.element()
            .bind_visibility_from(animation_select, "value", value="comet")
            .classes("w-full")
        )
        with comet_controls:
            apply_slider_with_label(
                comet_controls, comet_params, 0.01, 0.20, 0.01, "Speed:", "speed"
            )
            apply_color_input(comet_controls, comet_params, "Color:", "color")
            apply_color_input(
                comet_controls,
                comet_params,
                "Background Color:",
                "background_color",
            )
            apply_slider_with_label(
                comet_controls,
                comet_params,
                0,
                100,
                1,
                "Tail Length:",
                "tail_length",
            )
            apply_checkbox_with_label(comet_controls, comet_params, "Bounce", "bounce")
            apply_checkbox_with_label(
                comet_controls, comet_params, "Reverse", "reverse"
            )

        # Rainbow animation controls
        rainbow_controls = (
            ui.element()
            .bind_visibility_from(animation_select, "value", value="rainbow")
            .classes("w-full")
        )
        with rainbow_controls:
            apply_slider_with_label(
                rainbow_controls,
                rainbow_params,
                0.01,
                0.20,
                0.01,
                "Speed:",
                "speed",
            )
            apply_slider_with_label(
                rainbow_controls, rainbow_params, 1, 100, 1, "Period:", "period"
            )
            apply_slider_with_label(
                rainbow_controls, rainbow_params, 1, 100, 1, "Step:", "step"
            )
            apply_checkbox_with_label(
                rainbow_controls,
                rainbow_params,
                "Precompute Rainbow",
                "precompute_rainbow",
            )

        # Start and Stop buttons
        with ui.row().classes("mx-auto mt-4"):
            ui.button("Stop", on_click=stop_animation).style("border-radius: 25px")
            ui.button(
                "Start", on_click=lambda: start_animation(animation_select)
            ).style("border-radius: 25px")


ui.run()
