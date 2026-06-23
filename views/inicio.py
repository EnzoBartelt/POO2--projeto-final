from tkinter import *
from tkinter.ttk import *

from controllers.sistema import Sistema


class PainelInicio(Frame):
    def __init__(self, master, sistema: Sistema):
        # super().__init__(master)
        super().__init__(master, style="Custom.TFrame")
        self.pack(fill=BOTH, expand=True)

        self.sistema = sistema

        self.text = Text(self, height=3)
        self.text.pack(anchor=CENTER, expand=True)

        self.submit = Button(self, text="Enviar", command=self._gerar_recomendacoes)
        self.submit.pack(anchor=CENTER)

    def _gerar_recomendacoes(self):
        text = ", ".join(
            midia.get_titulo() for midia in self.sistema.gerar_recomendacoes()
        )
        self.res = Label(self, text=text)
        self.res.pack(anchor=CENTER)
