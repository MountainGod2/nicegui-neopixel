from nicegui import ui

ui.tab.default_style("min-height: 15%; padding-left: 2rem;")
ui.tab.default_classes("justify-start")
ui.label.default_style("color: rgb(250,66,125);")


@ui.page(path="/")
def index():
    ui.colors(primary="#fa427d")
    with ui.card().tight().style(
        "height: 90vh; width: 90vw; background: rgb(255,188,210); border-radius: 15px; border: 4px solid rgb(250,66,125);"
    ).classes("no-shadow"):
        with ui.splitter(value=20, limits=(20, 20)).classes("w-full").style(
            "height: 100%; width: 100%; background: transparent; border-radius: 8px; border: none;"
        ) as splitter:
            with splitter.before:
                with ui.tabs().props(
                    "vertical inline-label indicator-color='primary'"
                ).classes("w-full h-full border-[0px] no-shadow").style(
                    "background: rgb(250,66,125); background: linear-gradient(0deg, rgba(250,66,125,1) 0%, rgba(255,148,182,1) 70%); border-radius: 10px 0px 0px 10px;"
                ) as tabs:
                    ui.element().style("min-height: 27.5%;")
                    mail = ui.tab("Mails", icon="mail")
                    alarm = ui.tab("Alarms", icon="alarm")
                    movie = ui.tab("Movies", icon="movie")

            with splitter.after:
                with ui.tab_panels(tabs, value=mail, animated=False).props(
                    "vertical"
                ).classes("w-full h-full").style("background: transparent;"):
                    with ui.tab_panel(mail):
                        ui.label("Mails").classes("text-h5").style(
                            "font-weight: bold; font-size: 24px;"
                        )  # Increase label font size
                        ui.label("Content of mails")
                    with ui.tab_panel(alarm):
                        ui.label("Alarms").classes("text-h5").style(
                            "font-weight: bold; font-size: 24px;"
                        )  # Increase label font size
                        ui.label("Content of alarms")
                    with ui.tab_panel(movie):
                        ui.label("Movies").classes("text-h5").style(
                            "font-weight: bold; font-size: 24px;"
                        )  # Increase label font size
                        ui.label("Content of movies")


ui.run()
