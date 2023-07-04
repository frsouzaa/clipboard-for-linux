import keyboard
from os import popen, path
from pyautogui import position, hotkey
from clipboard import copy
import PySimpleGUI as sg
from typing import List


class Clipboard():
    history: List


    def __init__(self) -> None:
        self.history = list()
        self.startListener()
        rootDirectory = path.split(path.realpath(__file__))[0]
        self.imageDirectory = path.join(rootDirectory,"images/")
        self.lineWidth = 45
        self.backgroundColor = "#1c1e23"


    def startListener(self) -> None:
        keyboard.add_hotkey("ctrl + c", self.formatBuffer)
        keyboard.add_hotkey("alt + n", self.display)
    

    def formatBuffer(self) -> None:
        string = popen("xsel -o").read()
        if not string or string == "\n":
            return
        if len(self.history) > 0 and string == self.history[0]:
            return
        self.history.insert(0, string)
        if len(self.history) > 10:
            self.history.pop()


    def display(self) -> None:
        sg.theme("DarkGrey13")
        # "DarkGrey13": {"BACKGROUND": "#1c1e23", "TEXT": "#cccdcf", "INPUT": "#272a31", "TEXT_INPUT": "#cccdcf", "SCROLL": "#313641",
        #            "BUTTON": ("#8b9fde", "#313641"), "PROGRESS": ("#cccdcf", "#272a31"), "BORDER": 1, "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0, }

        self.buildWindow()
        # first = True
        self.windowId = popen("xdotool getactivewindow").read()
        while True:
            # if first:
            #     first = False

            event, values = self.window.read(timeout=200)
            
            if not self.isActive():
                self.window.close()
                break

            if event in (None, "Exit", "Cancel", "escape"): 
                break

            if event.find("copyStr") == 0:
                index = event.split("copyStr")[1]
                copy(values[f"multilineStr{index}"])

            if event.find("pasteStr") == 0:
                self.window.close()
                index = event.split("pasteStr")[1]
                copy(values[f"multilineStr{index}"])
                hotkey("ctrl", "v")
                
            if event.find("deleteStr") == 0:
                index = int(event.split("deleteStr")[1])
                self.history[index] = None
                if self.history.count(None) == len(self.history):
                    self.window["defaultColumn"].update(visible=True)
                    self.window["mainColumn"].update(visible=False)
                else:
                    self.window[f"infoColumn{index}"].update(visible=False)
            
            if event.find("deleteAll") == 0:
                self.history.clear()
                self.window["defaultColumn"].update(visible=True)
                self.window["mainColumn"].update(visible=False)

        self.window.close()
        i = 0
        for _ in range(len(self.history)):
            if self.history[i] == None:
                self.history.pop(i)
            else:
                i += 1

    
    def buildWindow(self) -> None:
        location = position()
        content = [
            [
                sg.Column(
                    [
                        [
                            sg.Text(text="There is nothing copied...", background_color=self.backgroundColor, border_width=0, pad=(80, 10))
                        ]
                    ],
                    key="defaultColumn",
                    visible=len(self.history) == 0
                ),
                sg.Column(
                    [
                        [
                            sg.Column(
                                [
                                    [
                                        sg.pin(
                                            sg.Column(
                                                [
                                                    [
                                                        self.multiline(string, f"multilineStr{i}"),
                                                        self.button("copy", f"copyStr{i}", "Copy"),
                                                        self.button("paste", f"pasteStr{i}", "Paste"),
                                                        self.button("deleteOne", f"deleteStr{i}", "Delete"),
                                                        # sg.ButtonMenu(
                                                        #     "",
                                                        #     menu_def=["Copy", "Paste", "Delete"],
                                                        #     key=f"buttonMenu{i}"
                                                        # )
                                                    ]
                                                ],
                                                key=f"infoColumn{i}"
                                            )
                                        )
                                    ] for i, string in enumerate(self.history)
                                ]
                            )
                        ],
                        [
                            sg.Column(
                                [
                                    [
                                        self.button("deleteAll", "deleteAll", "Delete all")
                                    ]
                                ],
                                justification="r"
                            )
                        ]
                    ],
                    key="mainColumn",
                    visible=len(self.history) > 0
                )
            ]
        ]
        layout = [
            [
                sg.Column(content)
            ]
        ]

        self.window = sg.Window(title="Clipboard for Linux", layout=layout, margins=(10,10), finalize=True, location=location)
        self.window.bind("<Escape>", "escape")

    
    def getRows(self, string: str) -> int:
        rows = sum(
            [
                (len(i) // self.lineWidth + 1) if (len(i) % self.lineWidth) else len(i) // self.lineWidth 
                for i in string.split("\n")
            ]
        )
        return rows if rows <= 5 else 5
    

    def multiline(self, string: str, key: str) -> sg.Multiline:
        return sg.Multiline(
            default_text=string, 
            size=(self.lineWidth,self.getRows(string)), 
            pad=(8,8), 
            no_scrollbar=True,
            key=key
        )

    
    def button(self, imageName: str, key: str, tooltip: str) -> sg.Button:
        return sg.Button(
            image_subsample=2, 
            key=key, 
            image_source=f"{self.imageDirectory}/{imageName}.png", 
            tooltip=f"{tooltip}", 
            mouseover_colors=self.backgroundColor, 
            button_color=self.backgroundColor, 
            border_width=0
        )


    def isActive(self):
        return self.windowId == popen("xdotool getactivewindow").read()
