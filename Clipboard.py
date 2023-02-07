import keyboard
from os import popen
import PySimpleGUI as sg


class Clipboard():
    history: list


    def __init__(self) -> None:
        self.history = []
        self.startListener()


    def startListener(self) -> None:
        keyboard.add_hotkey("ctrl + c", self.formatarBuffer)
        keyboard.add_hotkey("alt + n", self.display)
    

    def formatarBuffer(self) -> None:
        string = popen("xsel -o").read()
        if not string:
            return
        if len(self.history) > 1 and string == self.history[-1]:
            return
        self.history.append(string)

    
    def display(self) -> None:
        if not self.history:
            return

        sg.theme('DarkGray13')

        textColumn = [
            [sg.Multiline(default_text=string, size=(40,self.getRows(string)), pad=(8,8), no_scrollbar=True)] for string in self.history[::-1]
        ]

        layout = [
            [
                sg.Column(textColumn)
            ]
        ]

        self.window = sg.Window(title="Clipboard for Linux", layout=layout, margins=(10,10))

        while True:
            event, values = self.window.read()
            if event in (None, 'Exit', 'Cancel'): 
                break
        self.window.close()

    
    def getRows(self, string: str) -> int:
        return string.count("\n")+1
