import openpyxl
import pyperclip

import pyautogui, time
from time import sleep

# after starting to run the code, this gives me 5 seconds to navigate to my browser window
sleep(5)

# ---------------------------------------------
# Grab the patient's MRN from the master excel sheet, and copy to the clipboard
n = 4
while n < 28:
    workbook = openpyxl.load_workbook('input.xlsx')
    worksheet = workbook['Sheet1']
    cell = worksheet[f'A{n}']
    value = cell.value
    pyperclip.copy(value)
    print(f'Working on patient MRN {value}, number {n}')
    sleep(0.1)

    # ---------------------------------------------
    # Paste the MRN into the EMR search bar, and navigate to the patient's chart
    pyautogui.moveTo(450, 160, duration=0.25)
    sleep(0.5)
    pyautogui.click()
    sleep(0.5)
    pyautogui.hotkey('command', 'v')
    sleep(2)
    pyautogui.moveTo(760, 270, duration=0.25)
    sleep(0.5)
    pyautogui.click()
    sleep(3)

    # ---------------------------------------------
    # this convoluted bit below clicks in a number of places to
    # get rid of any warning popup boxes, if they appear on entering the chart.
    # If it doesn't click the popup box button, the clicks do nothing. Like an ex-parrot.
    # This is specific to my display, which is 1,440 x 900

    i = 1
    while i < 4:
        print(f'clicking down the line, run number {i}')
        pyautogui.moveTo(793, 660, duration=0.5)
        sleep(0.1)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(793, 690, duration=0.1)
        sleep(0.1)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(793, 720, duration=0.1)
        sleep(0.1)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(793, 750, duration=0.1)
        sleep(0.1)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(793, 780, duration=0.1)
        sleep(0.1)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(793, 810, duration=0.1)
        sleep(0.1)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(793, 840, duration=0.1)
        sleep(0.1)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(793, 870, duration=0.1)
        sleep(0.1)
        pyautogui.click()
        sleep(0.1)
        i = i + 1

    # ---------------------------------------
    # This clicks into the encouters section of the patient's chart

    pyautogui.moveTo(680, 480, duration=0.25)
    sleep(0.1)
    pyautogui.click()
    sleep(2)

    pyautogui.moveTo(1200, 240, duration=0.25)
    sleep(0.1)
    pyautogui.click()
    sleep(1)

    pyautogui.moveTo(468, 349, duration=0.25)
    sleep(0.1)
    pyautogui.click()
    sleep(0.1)

    pyautogui.moveTo(860, 410, duration=0.25)
    sleep(0.1)
    pyautogui.click()
    sleep(3)

    # ---------------------------------------
    # This copies the entire encounter history into a new text doc,
    # and saves it to your current working directory, titled with the MRN

    pyautogui.hotkey('command', 'a')
    sleep(0.5)
    pyautogui.hotkey('command', 'c')
    sleep(0.5)
    clipboard_content = pyperclip.paste()
    with open(f'{value}.txt', 'w') as file:
        file.write(clipboard_content)
    sleep(0.5)
    pyautogui.hotkey('command', 'w')
    sleep(1)
    n = n + 1
    # ---------------------------------------

print('DONE')

# ---------------------------------------
