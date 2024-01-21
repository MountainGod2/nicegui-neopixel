[nicegui-neopixel.webm](https://github.com/MountainGod2/nicegui-neopixel/assets/88257202/cc7c5027-474f-47a4-9bb3-3f0e3e805567)
# LED Strip Control with NiceGUI and NeoPixel

## Description
This project provides a web-based user interface for controlling an LED strip using the NiceGUI interface with a NeoPixel LED strip on an Adafruit board. The application allows users to select a digital pin, set the number of LEDs, adjust the brightness, and choose colors for the LED strip.

## Installation

### Prerequisites
- Python 3.6 or higher
- Adafruit board with NeoPixel LED strip connected

### Dependencies
- `board`
- `neopixel`
- `nicegui`
- `webcolors`

Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### Setting Up
1. Clone the repository or download the `main.py` file.
2. Connect the NeoPixel LED strip to the Adafruit board.

## Usage
Run the application by executing the `main.py` script:
```bash
python main.py
```
Navigate to the displayed URL in your web browser to access the user interface.

## Features
- Select any digital pin available on your Adafruit board.
- Set the number of LEDs in your strip.
- Adjust the brightness of the LED strip.
- Pick a color using a color picker, which will reflect on the LED strip and UI theme.
- Turn off the LEDs with a single button click.

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
