# OCT GUI Exporter
An **unofficial** tool for exporting OCT images and analyses from proprietary manufacturer software through GUI automation. Currently supports Zeiss Cirrus HD-OCT Review software ONLY, although the concepts are easily transferable.


## Prerequisites
1. The host machine (and/or any remote desktop sessions) must be running at a screen resolution of **1920x1080 px**.
2. The host machine must be running **Windows 11** or **Windows 10**. Most recently, this script has been developed and tested on Windows 11. Windows 10 should work as well, although full testing hasn't been done. 
3. Zeiss Cirrus HD-OCT Review software must be installed on the host machine.
4. Python must be installed on the host machine.

This script has been tested on Windows 11 with Python 3.13.


## Installation
1. Clone this repository
2. Run `pip install -r requirements.txt`
3. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract/releases/)
    - change path in `utils.py` if necessary


## Usage
1. Prepare `input.txt`, e.g.:
    ```
    CZMI1111111111 OD
    CZMI1111111111 OS
    CZMI2222222222 OD
    CZMI2222222222 OS
    CZMI3333333333 OD
    ...
    ```
2. Open Zeiss HD-OCT Review software, log in, and navigate to the main patient "search" screen.
3. Open `cmd` (or any terminal) **with administrator privileges** and navigate to this repository.
3. Run `python main.py`. In the next 3 seconds, open the Cirrus window in **maximized** mode in the **foreground**.
4. From this point on, the script will do the rest. It should start typing in CZMIs, opening patient charts, and running export sequences. To interrupt it, either use the PyAutoGUI failsafe (move the mouse to the very top left corner) or open the terminal that is running the script and keep pressing `Ctrl + C`.


## Contributions
This script was initially developed for use as an internal lab tool. Please forgive any poorly written or poorly designed code! **Contributions are welcome!** Please ensure that you have tested your code rigorously prior to committing it, and ideally add comments that document what conditions are necessary to run your code.


#### Areas for Improvement
- [ ] Improve OCR. Currently, it is very sensitive to whitespace and a bit unreliable.
- [ ] Improve general error-handling. Currently, one patient with a corrupt image or chart can derail the entire export sequence. A robust way to handle unexpected errors would be great.
- [ ] Support more image types. Currently, only export sequences for a limited number of image types are programmed.

... and many more! Please feel free to **file an issue**, although it may not be resolved, to document feature requests, etc.


## **Legal Disclaimer**
All work here is **unofficial** and **NOT** related to or endorsed by any OCT machine/software creators! All trademarks belong to their respective owners (e.g., Carl Zeiss Meditec AG).
