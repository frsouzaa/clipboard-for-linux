import keyboard
from os import popen
import PySimpleGUI as sg


class Clipboard():
    history: list


    def __init__(self) -> None:
        self.history = []
        self.startListener()
        self.display()


    def startListener(self) -> None:
        keyboard.add_hotkey("ctrl + c", self.formatarBuffer)
    

    def formatarBuffer(self) -> None:
        self.history.append(popen("xsel -o").read())
        print(self.history)

    
    def display(self) -> None:
        sg.theme('DarkGray13')

        textColumn = [
            [sg.InputText(default_text="teste", size=(20,20))]
        ]

        layout = [
            [
                sg.Column(textColumn)
            ]
        ]

        self.window = sg.Window(title="Clipboard for Linux", layout=layout, margins=(100,100))
        self.window.read()
