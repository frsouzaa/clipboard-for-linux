import keyboard
from os import popen, path
import PySimpleGUI as sg
from pyautogui import position, hotkey
from clipboard import copy


class Clipboard():
    history: list


    def __init__(self) -> None:
        self.history = []
        self.startListener()
        rootDirectory = path.split(path.realpath(__file__))[0]
        self.imageDirectory = path.join(rootDirectory,"images/")
        self.lineWidth = 45
        self.backgroundColor = "#1c1e23"


    def startListener(self) -> None:
        keyboard.add_hotkey("ctrl + c", self.formatarBuffer)
        keyboard.add_hotkey("alt + n", self.display)
    

    def formatarBuffer(self) -> None:
        string = popen("xsel -o").read()
        if not string or string == "\n":
            return
        if len(self.history) > 0 and string == self.history[0]:
            return
        self.history.insert(0, string)
        if len(self.history) > 10:
            self.history.pop()


    def display(self) -> None:
        sg.theme('DarkGrey13')
        # "DarkGrey13": {"BACKGROUND": "#1c1e23", "TEXT": "#cccdcf", "INPUT": "#272a31", "TEXT_INPUT": "#cccdcf", "SCROLL": "#313641",
        #            "BUTTON": ("#8b9fde", "#313641"), "PROGRESS": ("#cccdcf", "#272a31"), "BORDER": 1, "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0, }

        self.buildWindow()
        first = True
        while True:
            if first:
                self.windowId = popen("xdotool getactivewindow").read()
                first = False

            event, values = self.window.read(timeout=200)
            
            if not self.isActive():
                self.window.close()
                break

            if event in (None, 'Exit', 'Cancel'): 
                break
            
            if event.find("copyStr") == 0:
                copy(self.history[int(event.split("copyStr")[1])])

            if event.find("pasteStr") == 0:
                self.window.close()
                copy(self.history[int(event.split("pasteStr")[1])])
                hotkey("ctrl", "v")
                
            if event.find("deleteStr") == 0:
                self.history.pop(int(event.split("deleteStr")[1]))
                if not self.history:
                    break
                location = self.window.CurrentLocation(more_accurate=True)
                self.window.close()
                self.buildWindow(location=location)
            
            if event.find("deleteAll") == 0:
                self.history.clear()
                break

        self.window.close()

    
    def buildWindow(self, location: tuple = ()) -> None:
        if not location:
            location = position()
        if not self.history:
            textColumn = [
                [
                    sg.Text(text="You haven't copied nothing.", background_color=self.backgroundColor, border_width=0, pad=(80, 10))
                ]
            ]
        else:
            textColumn = [
                [
                    self.multiline(string),
                    self.button("copy", f"copyStr{i}", "Copy"),
                    self.button("paste", f"pasteStr{i}", "Paste"),
                    self.button("deleteOne", f"deleteStr{i}", "Delete"),
                ] for i, string in enumerate(self.history)
            ]
            textColumn.insert(0, 
                [
                    sg.Push(),
                    self.button("deleteAll", "deleteAll", "Delete all")
                ]
            )
        layout = [
            [
                sg.Column(textColumn)
            ]
        ]

        self.window = sg.Window(title="Clipboard for Linux", layout=layout, margins=(10,10), finalize=True, location=location)

    
    def getRows(self, string: str) -> int:
        rows = sum([(len(i) // self.lineWidth + 1) if (len(i) % self.lineWidth) else len(i) // self.lineWidth for i in string.split("\n")])
        return rows if rows <= 5 else 5


    def multiline(self, string: str) -> sg.Multiline:
        return sg.Multiline(default_text=string, size=(self.lineWidth,self.getRows(string)), pad=(8,8), no_scrollbar=True)

    
    def button(self, imageName: str, key: str, tooltip: str) -> sg.Button:
        return sg.Button(image_subsample=2, key=key, image_source=f"{self.imageDirectory}/{imageName}.png", tooltip=f"{tooltip}", mouseover_colors=self.backgroundColor, button_color=self.backgroundColor, border_width=0)


    def isActive(self):
        return self.windowId == popen("xdotool getactivewindow").read()
