from tkinter import *
from tkinter.ttk import *

from controllers.sistema import Sistema
from views.inicio import PainelInicio


class App(Tk):
    def __init__(self, sistema: Sistema):
        super().__init__()
        self.title("Nome do App sei lá lol")

        self.sistema = sistema

        style = Style()
        style.configure("Custom.TFrame", font=("Arial", 12), background="blue")

        notebook = Notebook(self)
        notebook.add(PainelInicio(self, self.sistema), text="Início")
        # a decidir:
        # notebook.add(PainelInicio(), text="Avaliações")
        # notebook.add(PainelInicio(), text="Histórico")
        # notebook.add(PainelInicio(), text="Conta")
        notebook.pack(fill=BOTH, expand=True)

        self.mainloop()
