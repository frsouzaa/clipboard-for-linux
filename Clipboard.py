import keyboard
from os import popen, path
import PySimpleGUI as sg
from pyautogui import position
from clipboard import copy


class Clipboard():
    history: list


    def __init__(self) -> None:
        self.history = []
        self.startListener()
        rootDirectory = path.split(path.realpath(__file__))[0]
        self.imageDirectory = path.join(rootDirectory,"images/")
        self.lineWidth = 60


    def startListener(self) -> None:
        keyboard.add_hotkey("ctrl + c", self.formatarBuffer)
        keyboard.add_hotkey("alt + n", self.display)
    

    def formatarBuffer(self) -> None:
        string = popen("xsel -o").read()
        if not string:
            return
        if len(self.history) > 0 and string == self.history[0]:
            return
        self.history.insert(0, string)
        if len(self.history) > 10:
            self.history.pop()


    def display(self) -> None:
        if not self.history:
            return

        sg.theme('DarkGrey13')
        # "DarkGrey13": {"BACKGROUND": "#1c1e23", "TEXT": "#cccdcf", "INPUT": "#272a31", "TEXT_INPUT": "#cccdcf", "SCROLL": "#313641",
        #            "BUTTON": ("#8b9fde", "#313641"), "PROGRESS": ("#cccdcf", "#272a31"), "BORDER": 1, "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0, }

        textColumn = [
            [
                sg.Multiline(default_text=string, size=(self.lineWidth,self.getRows(string)), pad=(8,8), no_scrollbar=True), 
                sg.Button(image_subsample=2, key=f"str{i}", image_source=f"{self.imageDirectory}/copy.png", tooltip="Copy", mouseover_colors="#1c1e23", button_color="#1c1e23", border_width=0)
            ] for i, string in enumerate(self.history)
        ]

        layout = [
            [
                sg.Column(textColumn)
            ]
        ]

        self.window = sg.Window(title="Clipboard for Linux", layout=layout, margins=(10,10), finalize=True, location=position())

        while True:
            event, values = self.window.read(timeout=200)
            if event in (None, 'Exit', 'Cancel'): 
                break
            
            if event.find("str") == 0:
                copy(self.history[int(event.split("str")[1])])

        self.window.close()

    
    def getRows(self, string: str) -> int:
        return sum([(len(i) // 60 + 1) if (len(i) % 60) else len(i) // 60 for i in string.split("\n")])
