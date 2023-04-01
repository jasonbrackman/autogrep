from __future__ import annotations

import os
from time import sleep
from typing import TYPE_CHECKING

import openpyxl
import pyautogui
import pyperclip

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet

CLOSE = "w"
COPY = "c"
PASTE = "v"
SELECT_ALL = "a"


class AutoGrepException(Exception):
    pass


def get_worksheet(input_file: str) -> Worksheet:
    if os.path.exists(input_file) is False:
        raise AutoGrepException(f"Input file not found: {input_file}")

    with openpyxl.load_workbook(input_file) as workbook:
        worksheet = workbook["Sheet1"]
    return worksheet


def do_work(worksheet: Worksheet):
    # Grab the patient's MRN from the master Excel sheet, and copy to the clipboard
    for cell_index in range(4, 28):
        cell = worksheet[f"A{cell_index}"]
        value = cell.value
        pyperclip.copy(value)
        print(f"Working on patient MRN {value}, number {cell_index}")
        sleep(0.1)

        # ---------------------------------------------
        # Paste the MRN into the EMR search bar, and navigate to the patient's chart
        _move_and_click(450, 160, duration=0.25, s1=0.5, s2=0.5)
        _hotkey_command(PASTE, s1=2.0)
        _move_and_click(760, 270, duration=0.25, s1=0.5, s2=3.0)

        # ---------------------------------------------
        # this convoluted bit below clicks in a number of places to
        # get rid of any warning popup boxes, if they appear on entering the chart.
        # If it doesn't click the popup box button, the clicks do nothing. Like an ex-parrot.
        # This is specific to my display, which is 1,440 x 900

        steps = [
            # x   y   dur.  s1   s2
            (793, 660, 0.5, 0.1, 0.1),
            (793, 690, 0.1, 0.1, 0.1),
            (793, 720, 0.1, 0.1, 0.1),
            (793, 750, 0.1, 0.1, 0.1),
            (793, 780, 0.1, 0.1, 0.1),
            (793, 810, 0.1, 0.1, 0.1),
            (793, 840, 0.1, 0.1, 0.1),
            (793, 870, 0.1, 0.1, 0.1),
        ]
        for i in range(4):
            print(f"clicking down the line, run number {i}")
            for x, y, duration, s1, s2 in steps:
                _move_and_click(x, y, duration=duration, s1=s1, s2=s2)

        # ---------------------------------------
        # This clicks into the encounters section of the patient's chart
        steps = [
            # x    y    dur.  s1  s2
            (680, 480, 0.25, 0.1, 2),
            (1200, 240, 0.25, 0.1, 1),
            (468, 349, 0.25, 0.1, 0.1),
            (860, 410, 0.25, 0.1, 3),
        ]
        for x, y, duration, s1, s2 in steps:
            _move_and_click(x, y, duration=duration, s1=s1, s2=s2)

        # ---------------------------------------
        # This copies the entire encounter history into a new text doc,
        # and saves it to your current working directory, titled with the MRN
        _hotkey_command(SELECT_ALL, s1=0.5)
        _hotkey_command(COPY, s1=0.5)

        clipboard_content = pyperclip.paste()
        with open(f"{value}.txt", "w") as file:
            file.write(clipboard_content)
        sleep(0.5)

        _hotkey_command(CLOSE, s1=1.0)


def _hotkey_command(command: str, s1=0.0):
    pyautogui.hotkey("command", command)
    sleep(s1)


def _move_and_click(x, y, duration=0.0, s1=0.0, s2=0.0):
    pyautogui.moveTo(x, y, duration=duration)
    sleep(s1)
    pyautogui.click()
    sleep(s2)


if __name__ == "__main__":
    sleep(5)  # gives me 5 seconds to navigate to my browser window
    ws = get_worksheet("input.xlsx")
    do_work(ws)

    print("DONE")
