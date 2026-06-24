'''
from tkinter import *
from tkinter.ttk import *
'''
import customtkinter as ctk
import re
import threading
import requests
from PIL import Image, ImageTk
from io import BytesIO
from time import sleep

from controllers.sistema import Sistema
from views.inicio import PainelInicio

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w200"

ctk.set_appearance_mode("dark")

'''
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
'''

class App(ctk.CTk):
    def __init__ (self):
        super().__init__()
        self._sistema = Sistema()

        self.title("Super avaliador de filmes")
        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()
        self.geometry(f"{largura}x{altura}+0+0")

        self._mostrar_tela("login")

    def _mostrar_tela(self, tela : str):
        for widget in self.winfo_children():
            widget.destroy()

        match tela:
            case "login":
                TelaLogin(self, self._sistema, lambda: self._mostrar_tela("principal"))
            case "principal":
                TelaPrincipal(self, self._sistema)

class TelaLogin(ctk.CTkFrame):
    def __init__(self, app : App, sistema: Sistema, callback):
        super().__init__(app)
        self._app = app
        self._sistema = sistema
        self._callback = callback
        self._construir_layout()

    def _construir_layout(self):
        centro = ctk.CTkFrame(self._app)
        centro.pack(expand=True)

        entry_nome = ctk.CTkEntry(centro, placeholder_text="Nome de usuário ou email", width=300, height=40, font=("Arial", 16))
        entry_nome.pack(pady=(20, 10), padx=20)
        entry_senha = ctk.CTkEntry(centro, placeholder_text="Senha", width=300, height=40, font=("Arial", 16))
        entry_senha.pack(pady=10, padx=20)
        erro = ctk.CTkLabel(centro, text="", text_color="red", font=("Arial", 12))
        erro.pack()

        botao_login = ctk.CTkButton(centro, text="Fazer login", width=300, height=40, font=("Arial", 14, "bold"), command=lambda: self._confirmar_login(entry_nome, entry_senha, erro))
        botao_login.pack(pady=(10, 5))
        botao_registrar = ctk.CTkLabel(centro, text="Registrar novo usuário", text_color="white", font=("Arial", 12))
        botao_registrar.pack(pady=(0, 10))
        botao_registrar.bind("<Enter>", lambda e: (botao_registrar.configure(text_color="gray"), botao_registrar.configure(cursor="hand2")))
        botao_registrar.bind("<Leave>", lambda e: (botao_registrar.configure(text_color="white"), botao_registrar.configure(cursor="")))
        botao_registrar.bind("<Button 1>", lambda e: self._registrar(centro))

    def _confirmar_login(self, nome, senha, erro):
        if not nome.get() and not senha.get():
            nome.configure(border_color="red")
            senha.configure(border_color="red")
            erro.configure(text="Preencha todos os campos para continuar")
            return
        elif not nome.get():
            nome.configure(border_color="red")
            senha.configure(border_color="gray")
            erro.configure(text="Preencha todos os campos para continuar")
            return
        elif not senha.get():
            nome.configure(border_color="gray")
            senha.configure(border_color="red")
            erro.configure(text="Preencha todos os campos para continuar")
            return
        else:
            nome.configure(border_color="gray")
            senha.configure(border_color="gray")
            erro.configure(text="")

        try:
            if self._sistema.logar(nome.get().strip(), senha.get().strip()):
                self._callback()
            else:
                erro.configure(text="Usuário ou senha incorretos")
        except Exception as e:
            erro.configure(text=f"{e}")


    def _registrar(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        entry_nome = ctk.CTkEntry(frame, placeholder_text="Nome de usuário", width=300, height=40, font=("Arial", 16))
        entry_nome.pack(pady=(20, 10), padx=20)
        entry_email = ctk.CTkEntry(frame, placeholder_text="Email", width=300, height=40, font=("Arial", 16))
        entry_email.pack(pady=10, padx=20)
        entry_senha = ctk.CTkEntry(frame, placeholder_text="Senha", width=300, height=40, font=("Arial", 16))
        entry_senha.pack(pady=10, padx=20)

        avaliar_senha = ctk.CTkLabel(frame, text="A senha deve conter ao menos:", font=("Arial", 14))
        avaliar_senha.pack(anchor="w", padx=20)
        qtd = ctk.CTkLabel(frame, text="• 8 caracteres", text_color="red", font=("Arial", 12))
        qtd.pack(anchor="w", padx=20)
        maiusculas = ctk.CTkLabel(frame, text="• Uma letra maiúscula", text_color="red", font=("Arial", 12))
        maiusculas.pack(anchor="w", padx=20)
        minusculas = ctk.CTkLabel(frame, text="• Uma letra minúscula", text_color="red", font=("Arial", 12))
        minusculas.pack(anchor="w", padx=20)
        numeros = ctk.CTkLabel(frame, text="• Um número", text_color="red", font=("Arial", 12))
        numeros.pack(anchor="w", padx=20)
        especiais = ctk.CTkLabel(frame, text="• Um caractere especial", text_color="red", font=("Arial", 12))
        especiais.pack(anchor="w", padx=20)

        entry_senha.bind("<KeyRelease>", lambda e: (
            qtd.configure(text_color="green" if len(entry_senha.get()) >= 8 else "red"),
            maiusculas.configure(text_color="green" if re.search(r"[A-Z]", entry_senha.get()) else "red"),
            minusculas.configure(text_color="green" if re.search(r"[a-z]", entry_senha.get()) else "red"),
            numeros.configure(text_color="green" if re.search(r"[0-9]", entry_senha.get()) else "red"),
            especiais.configure(text_color="green" if re.search(r"[^A-Za-z0-9]", entry_senha.get()) else "red")
        ))

        entry_confirmar_senha = ctk.CTkEntry(frame, placeholder_text="Confirmar senha", width=300, height=40, font=("Arial", 16))
        entry_confirmar_senha.pack(pady=10, padx=20)
        erro = ctk.CTkLabel(frame, text="", text_color="red", font=("Arial", 12))
        erro.pack()

        botao_registrar = ctk.CTkButton(frame, text="Confirmar", width=300, height=40, font=("Arial", 14, "bold"), command=lambda: self._confirmar_registro(entry_nome, entry_email, entry_senha, entry_confirmar_senha, erro))
        botao_registrar.pack(pady=10)

    def _confirmar_registro(self, nome, email, senha, confirma_senha, erro):
        campos = [nome, email, senha, confirma_senha]

        for campo in campos:
            campo.configure(border_color="gray")

        vazios = [campo for campo in campos if not campo.get()]

        if vazios:
            for campo in campos:
                if campo in vazios:
                    campo.configure(border_color="red")
                else:
                    campo.configure(border_color="gray")
            erro.configure(text="Preencha todos os campos para continuar")
            return
        
        if senha.get() != confirma_senha.get():
            senha.configure(border_color="red")
            confirma_senha.configure(border_color="red")
            erro.configure(text="As senhas não coincidem")
            return

        try:
            if self._sistema.cadastrar(nome.get().strip(), email.get().strip(), senha.get().strip()):
                erro.configure(text="Usuário criado com sucesso", text_color="green")
                sleep(1)
                self._app._mostrar_tela("login")
        except Exception as e:
            erro.configure(text=f"{e}")

class TelaPrincipal(ctk.CTkFrame):
    def __init__ (self, app : App, sistema : Sistema):
        super().__init__(app)
        self._app = app
        self._sistema = sistema
        self.pack(expand=True, fill="both")
        self._construir_layout()

    def _construir_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        hotbar = ctk.CTkFrame(self, height=60)
        hotbar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        hotbar.grid_propagate(False)

        esquerdo = PainelEsquerdo(self, self._sistema)
        esquerdo.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        direito = PainelDireito(self, self._sistema)
        direito.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

class PainelEsquerdo(ctk.CTkFrame):
    def __init__(self, pai : ctk.CTkFrame, sistema : Sistema):
        super().__init__(pai)
        self._sistema = sistema
        self.grid_propagate(False)
        self._carregar()

    def _carregar(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        entry_buscar = ctk.CTkEntry(self, placeholder_text="Pesquise por filmes ou séries", height=40, width=600)
        entry_buscar.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        botao_buscar = ctk.CTkButton(self, text="Buscar", width=100, height=40, command=lambda: self._buscar(self, entry_buscar))
        botao_buscar.grid(row=1, column=1, sticky="e", padx=(5, 10), pady=10)

class PainelDireito(ctk.CTkFrame):
    def __init__(self, pai : ctk.CTkFrame, sistema : Sistema):
        super().__init__(pai)
        self._sistema = sistema
        self._carregar()
    
    def _carregar(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        entry_buscar = ctk.CTkEntry(self, placeholder_text="Pesquise por filmes ou séries", height=40, width=600)
        entry_buscar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        botao_buscar = ctk.CTkButton(self, text="Buscar", width=100, height=40, command=lambda: self._buscar(self, entry_buscar))
        botao_buscar.grid(row=0, column=1, sticky="e", padx=(5, 10), pady=10)

        self._label_status = ctk.CTkLabel(self, text="Carregando...", text_color="gray")
        self._label_status.grid(row=1, column=0, columnspan=2)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=2, column=0, columnspan=2, sticky="nsew")

        self._secao_trending = SecaoMidias(container, "Em alta")
        self._secao_trending.pack(fill="x")

        self._secao_upcoming = SecaoMidias(container, "Em breve")
        self._secao_upcoming.pack(fill="x")

        self.after(100, self._carregar_inicial)

    def _carregar_inicial(self):
        thread = threading.Thread(target=self._worker_inicial, daemon=True)
        thread.start()

    def _worker_inicial(self):
        try:
            trending = self._sistema.trending()
            upcoming = self._sistema.upcoming()

            self.after(0, self._exibir_inicial, trending, upcoming)
        except Exception as e:
            self.after(0, self._label_status.configure, {"text": f"Erro ao carregar: {e}"})

    def _exibir_inicial(self, trending, upcoming):
        self._label_status.destroy()
        self._secao_trending.exibir(trending, comando=self._ao_clicar_midia)
        self._secao_upcoming.exibir(upcoming, comando=self._ao_clicar_midia)

    def _ao_clicar_midia(self, midia):
        print(f"Clicou em: {midia.get_titulo()}")

    def _exibir_resultados(self, midias):
        self._label_status.grid_remove()

        for widget in self._frame_resultados.winfo_children():
            widget.destroy()

        for midia in midias:
            ctk.CTkLabel(self._frame_resultados, text=midia.get_titulo()).pack(anchor="w", pady=2)

    def _buscar(self, frame, entry):
        pass

class CardMidia(ctk.CTkFrame):
    def __init__(self, pai, midia, comando=None):
        super().__init__(pai, width=160, cursor="hand2")
        self._altura = 195
        self._largura = 130
        self._midia   = midia
        self._comando = comando
        self._img_ref = None
        self._construir()
        self._carregar_poster()

    def _construir(self):
        self._label_poster = ctk.CTkLabel(
            self,
            text="",
            width=self._largura,
            height=self._altura,
            fg_color="#3a3a3a"
        )
        self._label_poster.pack(padx=6, pady=(6, 2))

        ctk.CTkLabel(
            self,
            text=self._midia.get_titulo(),
            font=("Arial", 12, "bold"),
            wraplength=self._largura - 12,
            justify="center"
        ).pack(padx=6)

        rodape = ctk.CTkFrame(self, fg_color="transparent", width=self._largura)
        rodape.pack(padx=6, pady=(2, 6))

        ano = (self._midia.get_data_lancamento() or "")[:4]
        ctk.CTkLabel(rodape, text=ano, font=("Arial", 11), text_color="gray").pack(side="left", padx=(0, 10))

        nota = self._midia.get_avaliacoes()
        nota_texto = f"{nota:.1f}" if nota else ""
        ctk.CTkLabel(rodape, text=nota_texto, font=("Arial", 11), text_color="#f5c518").pack(side="right", padx=(10, 0))

        self._bind_clique(self)

    def _bind_clique(self, widget):
        if self._comando:
            widget.bind("<Button-1>", lambda e: self._comando(self._midia))
            for filho in widget.winfo_children():
                self._bind_clique(filho)

    def _carregar_poster(self):
        path = self._midia.get_poster_path()
        if not path:
            return
        thread = threading.Thread(target=self._worker_poster, args=(path,), daemon=True)
        thread.start()

    def _worker_poster(self, path):
        try:
            url = TMDB_IMAGE_BASE + path
            resposta = requests.get(url, timeout=5)
            resposta.raise_for_status()
            imagem = Image.open(BytesIO(resposta.content))
            imagem = imagem.resize((self._largura, self._altura))
            ctk_img = ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(self._largura, self._altura))
            self.after(0, self._aplicar_poster, ctk_img)
        except Exception:
            pass

    def _aplicar_poster(self, ctk_img):
        self._img_ref = ctk_img 
        self._label_poster.configure(image=ctk_img, text="")


class SecaoMidias(ctk.CTkFrame):
    def __init__(self, pai, titulo_secao: str):
        super().__init__(pai, fg_color="transparent")
        self._n = 7
        self._titulo_secao = titulo_secao
        self._frame_cards  = None
        self._construir()

    def _construir(self):
        ctk.CTkLabel(
            self,
            text=self._titulo_secao,
            font=("Arial", 15, "bold"),
            anchor="w"
        ).pack(fill="x", padx=10, pady=(10, 4))

        self._frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_cards.pack(fill="x", padx=10)

        for i in range(self._n):
            self._frame_cards.grid_columnconfigure(i, weight=1, uniform="card", minsize=130)


    def exibir(self, midias: list, comando=None):
        for widget in self._frame_cards.winfo_children():
            widget.destroy()

        for i, midia in enumerate(midias[:self._n]):
            card = CardMidia(self._frame_cards, midia, comando=comando)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="n")