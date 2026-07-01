import customtkinter as ctk
import re
import threading
from queue import Empty, Queue
import requests
from PIL import Image
from io import BytesIO
from time import sleep

from models.midia import *
from controllers.sistema import Sistema

# Endereço base para carregar os posters 
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w200"

ctk.set_appearance_mode("dark") # Define o estilo padrão do CustomTKinter para "dark"

# Classe principal do App, cria a janela base onde serão posicionadas todas as páginas do programa
class App(ctk.CTk):
    def __init__ (self):
        super().__init__()
        self._sistema = Sistema()

        self.title("Super avaliador de filmes")
        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()
        self.geometry(f"{largura-100}x{altura-100}+0+0")

        self._mostrar_tela("login")

    def _mostrar_tela(self, tela : str):
        for widget in self.winfo_children():
            widget.destroy()

        match tela: # Duas opções de tela, uma para o login e a página principal para qual o usuário é redirecionado quando realiza o login
            case "login":
                TelaLogin(self, self._sistema, lambda: self._mostrar_tela("principal"))
            case "principal":
                TelaPrincipal(self, self._sistema)

# Tela de login, chamada quando a aplicação é iniciada
class TelaLogin(ctk.CTkFrame):
    # Recebe o app como master, o qual estará posicionado dentro, o sistema para realização de ações com o restante da aplicação, e uma função de
    # callback, que no caso é a chamada no caso de login bem sucedido (redirecionamento para a página principal)
    def __init__(self, app : App, sistema: Sistema, callback): 
        super().__init__(app)
        self._app = app
        self._sistema = sistema
        self._callback = callback
        self._construir_layout()

    # Constrói a página padrão de login
    def _construir_layout(self):
        centro = ctk.CTkFrame(self._app)
        centro.pack(expand=True)

        # Campos de entrada
        entry_nome = ctk.CTkEntry(centro, placeholder_text="Nome de usuário ou email", width=300, height=40, font=("Arial", 16))
        entry_nome.pack(pady=(20, 10), padx=20)
        entry_senha = ctk.CTkEntry(centro, placeholder_text="Senha", width=300, height=40, font=("Arial", 16))
        entry_senha.pack(pady=10, padx=20)
        erro = ctk.CTkLabel(centro, text="", text_color="red", font=("Arial", 12))
        erro.pack()

        # Botões para login e cadastro, cada um com uma função de callback
        # Botão de login: quando apertado chama _confirmar_login para fazer validações de entrada e chamar o método necesário de Sistema
        botao_login = ctk.CTkButton(centro, text="Fazer login", width=300, height=40, font=("Arial", 14, "bold"), command=lambda: self._confirmar_login(entry_nome, entry_senha, erro))
        botao_login.pack(pady=(10, 5))
        # Botão de cadastro: chama _registrar que reconstrói a página para o cadastro
        botao_registrar = ctk.CTkLabel(centro, text="Registrar novo usuário", text_color="white", font=("Arial", 12))
        botao_registrar.pack(pady=(0, 10))
        # Atribuição para o botao_registrar funcionar como um "texto responsível" (basicamente um link)
        botao_registrar.bind("<Enter>", lambda e: (botao_registrar.configure(text_color="gray"), botao_registrar.configure(cursor="hand2")))
        botao_registrar.bind("<Leave>", lambda e: (botao_registrar.configure(text_color="white"), botao_registrar.configure(cursor="")))
        botao_registrar.bind("<Button 1>", lambda e: self._registrar(centro))

    # Chamada ao apertar o botão de login
    def _confirmar_login(self, nome, senha, erro):
        # Validação de entradas
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

        # Chamada do método de login do Sistema, em caso de sucesso chama o callback da classe (neste caso, a página principal)
        try:
            if self._sistema.logar(nome.get().strip(), senha.get().strip()):
                self._callback()
            else:
                # Em caso de falha, define a mensagem
                erro.configure(text="Usuário ou senha incorretos")
        except Exception as e:
            erro.configure(text=f"{e}")

    # Chamada quando o botão de registrar é apertado
    def _registrar(self, frame):
        # Limpa a página
        for widget in frame.winfo_children():
            widget.destroy()

        # Constrói as entradas necessárias para o cadastro
        entry_nome = ctk.CTkEntry(frame, placeholder_text="Nome de usuário", width=300, height=40, font=("Arial", 16))
        entry_nome.pack(pady=(20, 10), padx=20)
        entry_email = ctk.CTkEntry(frame, placeholder_text="Email", width=300, height=40, font=("Arial", 16))
        entry_email.pack(pady=10, padx=20)
        entry_senha = ctk.CTkEntry(frame, placeholder_text="Senha", width=300, height=40, font=("Arial", 16))
        entry_senha.pack(pady=10, padx=20)

        # Exibição da validação de senha, para noção do usuário
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

        # Bind para interatividade em real time da entrada da senha
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

        # Botão para confirmar, chama _confirmar_registro
        botao_registrar = ctk.CTkButton(frame, text="Confirmar", width=300, height=40, font=("Arial", 14, "bold"), command=lambda: self._confirmar_registro(entry_nome, entry_email, entry_senha, entry_confirmar_senha, erro))
        botao_registrar.pack(pady=10)

    # Chamada quando o botão de confirmar é ativado
    def _confirmar_registro(self, nome, email, senha, confirma_senha, erro):
        campos = [nome, email, senha, confirma_senha]

        # Define campos para cinza (caso já houvesse alguma tentativa com erro)
        for campo in campos:
            campo.configure(border_color="gray")

        vazios = [campo for campo in campos if not campo.get()] # Verifica campos vazios

        # Informa o erro
        if vazios:
            for campo in campos:
                if campo in vazios:
                    campo.configure(border_color="red")
                else:
                    campo.configure(border_color="gray")
            erro.configure(text="Preencha todos os campos para continuar")
            return
        
        # Verifica se as senhas são iguais
        if senha.get() != confirma_senha.get():
            senha.configure(border_color="red")
            confirma_senha.configure(border_color="red")
            erro.configure(text="As senhas não coincidem")
            return

        # Chama o método de cadastro do Sistema, em caso de sucesso volta para tela de login
        try:
            if self._sistema.cadastrar(nome.get().strip(), email.get().strip(), senha.get().strip()):
                erro.configure(text="Usuário criado com sucesso", text_color="green")
                sleep(1)
                self._app._mostrar_tela("login")
        except Exception as e:
            erro.configure(text=f"{e}")

# Classe da tela principal da aplicação, um frame dentro de app
class TelaPrincipal(ctk.CTkFrame):
    # Essa e todas as demais telas são frames dentro de App, e recebem app como referência de master e o Sistema 
    def __init__ (self, app : App, sistema : Sistema):
        super().__init__(app)
        self._app = app
        self._sistema = sistema
        self.pack(expand=True, fill="both")
        self._construir_layout()

    # Constrói a página principal, dividida em 3 seções: hotbar, painel esquerdo e painel direito
    def _construir_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=290)
        self.grid_columnconfigure(1, weight=2)

        hotbar = ctk.CTkFrame(self, height=60)
        hotbar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        hotbar.grid_propagate(False)

        # Como a hotbar não é dinâmica e nem alterada na aplicação, é apenas criada dentro da página inicial
        self._construir_hotbar(hotbar)

        # Os dois páines são classes próprias, defininindo sua exibição e atualizando seu conteúdo conforme necessário
        self.esquerdo = PainelEsquerdo(self, self._sistema)
        self.esquerdo.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.direito = PainelDireito(self, self._sistema)
        self.direito.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

    # Constrói a hotbar da página
    def _construir_hotbar(self, hotbar):
        self._menu_aberto = False
        self._janela_menu = None

        hotbar.grid_columnconfigure(1, weight=1)

        # Esquerda: ícone de menu, contém opções da aplicação (nesse caso, apenas deslogar)
        icone_menu = ctk.CTkButton(hotbar, text="☰", width=48, height=48, fg_color="transparent", hover_color="#333333", command=self._toggle_menu)
        icone_menu.grid(row=0, column=0, padx=(8, 0), pady=6)

        # Direita: ícone casa e botão recomendar
        frame_direita = ctk.CTkFrame(hotbar, fg_color="transparent")
        frame_direita.grid(row=0, column=2, padx=(0, 8), pady=6)

        # Botão que volta para página principal (reconstrói os painéis)
        self._btn_casa = ctk.CTkButton(frame_direita, text="⌂", font=("Arial", 20), width=48, height=48, fg_color="transparent", hover_color="#333333",command=self._ir_para_inicio)
        self._btn_casa.pack(side="left", padx=(0, 4))

        # Botão que abre o painel de recomendações (substitui o painel direito)
        ctk.CTkButton(frame_direita, text="Recomendar", height=36, command=self._abrir_painel_recomendacoes).pack(side="left")

    # Abre e fecha o menu flutuante (contém apenas opção de deslogar)
    def _toggle_menu(self):
        if self._menu_aberto and self._janela_menu and self._janela_menu.winfo_exists():
            self._janela_menu.destroy()
            self._menu_aberto = False
            return

        self._janela_menu = ctk.CTkToplevel(self)
        self._janela_menu.overrideredirect(True)   # sem borda/título
        self._janela_menu.attributes("-topmost", True)

        # Posiciona abaixo do botão de menu (canto superior esquerdo)
        x = self.winfo_rootx() + 8
        y = self.winfo_rooty() + 60
        self._janela_menu.geometry(f"180x50+{x}+{y}")

        ctk.CTkButton(self._janela_menu, text="Deslogar", fg_color="transparent", hover_color="#333333", anchor="w", command=self._deslogar).pack(fill="x", padx=4, pady=4)

        self._menu_aberto = True
        self._janela_menu.bind("<FocusOut>", lambda e: self._fechar_menu())

    # Fecha o menu flutuante
    def _fechar_menu(self):
        if self._janela_menu and self._janela_menu.winfo_exists():
            self._janela_menu.destroy()
        self._menu_aberto = False

    # Desloga o usuário (chama de Sistema)
    def _deslogar(self):
        self._fechar_menu()
        self._sistema.deslogar()
        self._app._mostrar_tela("login")

    # Botão que volta para o painel inicial (caso já não esteja)
    def _ir_para_inicio(self):
        if hasattr(self, "_no_inicio") and self._no_inicio:
            return
        self.direito.destroy()
        self.direito = PainelDireito(self, self._sistema)
        self.direito.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self._no_inicio = True

    # Instância o painel de recomendações quando o botão for clicado
    def _abrir_painel_recomendacoes(self):
        self.direito.destroy()
        self.direito = PainelRecomendacoes(self, self._sistema)  # a implementar
        self.direito.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self._no_inicio = False

# Painel esquerdo, exibe as informações das mídias assistidas pelo usuário
class PainelEsquerdo(ctk.CTkFrame):
    def __init__(self, pai : ctk.CTkFrame, sistema : Sistema):
        super().__init__(pai, width=290)
        self._n = 7 # Número de cards por linha
        self._pai = pai
        self._sistema = sistema
        self._fila_historico = Queue()
        self.grid_propagate(False)
        self._carregar()

    # Constrói o painel (exibe as informações conforme o usuário)
    def _carregar(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Assistidos", font=("Arial", 15, "bold"), anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 4))

        self._frame_cards = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._frame_cards.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 6))
        self._frame_cards.grid_columnconfigure(0, weight=1)

        entry_buscar = ctk.CTkEntry(self, placeholder_text="Pesquise por filmes ou séries", height=40, width=600)
        entry_buscar.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        botao_buscar = ctk.CTkButton(self, text="Buscar", width=60, height=40, command=lambda: self._buscar(entry_buscar))
        botao_buscar.grid(row=2, column=1, sticky="e", padx=(5, 10), pady=10)

        self.after(100, self._carregar_historico)

    # Cria uma thread secundária para não travar a aplicação enquanto os dados são carregados
    def _carregar_historico(self):
        thread = threading.Thread(target=self._worker_historico, daemon=True)
        thread.start()
        self.after(100, self._verificar_historico)

    # Worker da thread secundária chama as mídias do usuário de Sistema
    def _worker_historico(self):
        try:
            historico = self._sistema.carregar_midias()
            self._fila_historico.put(("ok", historico))
        except Exception as e:
            self._fila_historico.put(("erro", e))

    # Se o worker tiver obtido o histórico, segue para a exibição
    def _verificar_historico(self):
        try:
            status, resultado = self._fila_historico.get_nowait()
        except Empty:
            self.after(100, self._verificar_historico)
            return

        if status == "ok":
            self._exibir_historico(resultado)
        else:
            print(f"Erro ao carregar histórico: {resultado}")

    # Exibe as informações no painel
    def _exibir_historico(self, historico: dict):
        # Limpa o painel
        for widget in self._frame_cards.winfo_children():
            widget.destroy()

        # Se o histórico estiver vazio, isso é, o usuário não avaliou mídidas, exibe a mensagem de acordo
        if not historico:
            ctk.CTkLabel(self._frame_cards, text="Nenhuma mídia\navaliada ainda.", text_color="gray", justify="center").pack(pady=20)
            return

        # Cria cards clicáveis pra cada mídia no histórico
        for tmdb_id, dados in list(historico.items()):
            card = CardHistorico(self._frame_cards, midia=dados["midia"], avaliacao=dados["avaliacao"], comando=self._ao_clicar)
            card.grid(sticky="ew", pady=4, padx=4)

    # Ao clicar no card, exibe a página da mídia
    def _ao_clicar(self, midia):
        PaginaMidia(self._pai, sistema=self._sistema, midia=midia)

    # Chama o método de Sistema e faz a busca de acordo com a entrada do usuário
    def _buscar(self, entry):
        keyword = entry.get().strip()
        if not keyword:
            historico = self._sistema.carregar_midias()
        else:
            historico = self._sistema.buscar_historico(keyword)
        self._exibir_historico(historico)

    # Chamado após o usuário fazer uma nova avaliação.
    def atualizar(self):
        self._carregar_historico()

# Classe que cria um card no formato de exibição do painel esquerdo
class CardHistorico(ctk.CTkFrame):
    def __init__(self, pai, midia, avaliacao, comando=None):
        super().__init__(pai, cursor="hand2")
        self._largura = 40
        self._altura = 60
        self._midia     = midia
        self._avaliacao = avaliacao
        self._comando   = comando
        self._img_ref   = None
        self._fila_poster = Queue()
        self._construir()
        self._carregar_poster()

    # Constrói o card
    def _construir(self):
        self._label_poster = ctk.CTkLabel(self, text="", width=self._largura, height=self._altura)
        self._label_poster.pack(side="left", padx=(6, 8), pady=6)

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=6)

        ctk.CTkLabel(info, text=self._midia.get_titulo(), font=("Arial", 12, "bold"), wraplength=140, justify="left", anchor="w").pack(anchor="w")

        nota = self._avaliacao.get_nota()
        ctk.CTkLabel(info, text=f"★ {nota:.1f}", font=("Arial", 11), text_color="#f5c518", anchor="w").pack(anchor="w", pady=(2, 0))

        self._bind_clique(self)

    # Torna o card clicável
    def _bind_clique(self, widget):
        if self._comando:
            widget.bind("<Button-1>", lambda e: self._comando(self._midia))
            for filho in widget.winfo_children():
                self._bind_clique(filho)

    # Carrega o poster da mídia. O poster é coletado da web, então cria uma thread para não travar a aplicação enquanto busca
    def _carregar_poster(self):
        path = self._midia.get_poster_path()
        if not path:
            return
        thread = threading.Thread(target=self._worker_poster, args=(path,), daemon=True)
        thread.start()
        self.after(100, self._verificar_poster)

    # Worker da thread, busca o poster
    def _worker_poster(self, path):
        try:
            url = TMDB_IMAGE_BASE + path
            resposta = requests.get(url, timeout=5)
            resposta.raise_for_status()
            imagem = Image.open(BytesIO(resposta.content))
            imagem = imagem.resize((self._largura, self._altura))
            self._fila_poster.put(("ok", imagem))
        except Exception as e:
            self._fila_poster.put(("erro", e))

    # Verifica se o poster foi encontrado
    def _verificar_poster(self):
        try:
            status, resultado = self._fila_poster.get_nowait()
        except Empty:
            self.after(100, self._verificar_poster)
            return

        if status == "ok":
            self._aplicar_poster(resultado)

    # Coloca o poster no card
    def _aplicar_poster(self, imagem):
        try:
            ctk_img = ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(self._largura, self._altura))
            self._img_ref = ctk_img
            self._label_poster.configure(image=ctk_img, text="")
        except Exception:
            pass    

# Painel direito, exibe duas seções: Em alta e Em breve, pegando mídias com base na API do TMDB e nos respectivos endpoints
class PainelDireito(ctk.CTkFrame):
    def __init__(self, pai : ctk.CTkFrame, sistema : Sistema):
        super().__init__(pai)
        self._pai = pai
        self._sistema = sistema
        self._fila_carregamento = Queue()
        self._fila_busca = Queue()
        self._carregar()
    
    # Constrói o painel
    def _carregar(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        # Campo de busca
        entry_buscar = ctk.CTkEntry(self, placeholder_text="Pesquise por filmes ou séries", height=40, width=600)
        entry_buscar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        botao_buscar = ctk.CTkButton(self, text="Buscar", width=100, height=40, command=lambda: self._verifica_pagina(entry_buscar))
        botao_buscar.grid(row=0, column=1, sticky="e", padx=(5, 10), pady=10)

        # Mensagem de status
        self._label_status = ctk.CTkLabel(self, text="Carregando...", text_color="gray")
        self._label_status.grid(row=1, column=0, columnspan=2)

        # Frame das duas seções
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Instância as seções, que definem a exibição
        self._secao_trending = SecaoMidias(container, "Em alta")
        self._secao_trending.pack(fill="x")

        self._secao_upcoming = SecaoMidias(container, "Em breve")
        self._secao_upcoming.pack(fill="x")

        self.after(100, self._carregar_inicial)

    # Thread secundária para buscar as mídias da API
    def _carregar_inicial(self):
        thread = threading.Thread(target=self._worker_inicial, daemon=True)
        thread.start()
        self.after(100, self._verificar_carregamento)

    # Worker que busca as mídias
    def _worker_inicial(self):
        tentativas = 3 # 3 tentativas antes de continuar
        for i in range(tentativas):
            try:
                trending = self._sistema.trending() # Método de Sistema que retorna as mídias da API no endpoint /trending
                upcoming = self._sistema.upcoming() # Método de Sistema que retorna as mídias da API no endpoint /upcoming
                self._fila_carregamento.put(("ok", trending, upcoming))
                return
            except Exception as e:
                if i < tentativas - 1:
                    sleep(2)
                else:
                    self._fila_carregamento.put(("erro", e))

    # Verifica se foram encontradas mídias, e exibe as seções
    def _verificar_carregamento(self):
        try:
            resultado = self._fila_carregamento.get_nowait()
        except Empty:
            self.after(100, self._verificar_carregamento)
            return

        # Chama o método da seção que a constrói
        if resultado[0] == "ok":
            _, trending, upcoming = resultado
            self._label_status.destroy()
            self._secao_trending.exibir(trending or [], comando=self._ao_clicar)
            self._secao_upcoming.exibir(upcoming or [], comando=self._ao_clicar)
        else:
            _, erro = resultado
            print(f"Erro ao carregar mídias iniciais: {erro}")
            self._label_status.configure(text="Serviço temporariamente indisponível. Tente novamente.")

    # Ao clicar num card de mídia, abre a página da mídia
    def _ao_clicar(self, midia):
        PaginaMidia(self._pai, sistema=self._sistema, midia=midia)

    # Controla a exibição atual para a busca
    def _verifica_pagina(self, entry):
        if not entry.get():
            if self._secao_trending.winfo_exists() or self._secao_upcoming.winfo_exists():
                return
            self._carregar()
            return
        
        self._buscar(entry)

    # Chamada quando o botão de buscar é clicado, destrói as seções e faz chama a busca
    def _buscar(self, entry):
        self._label_status.destroy()
        self._secao_trending.destroy()
        self._secao_upcoming.destroy()
        self.after(100, self._carregar_busca, entry.get())

    # Thread secundária para buscar as mídias na API
    def _carregar_busca(self, entry : str):
        thread = threading.Thread(target=lambda: self._worker_busca(entry), daemon=True)
        thread.start()
        self.after(100, self._verificar_busca)

    # Worker realiza a busca, chamando o método de Sistema
    def _worker_busca(self, entry : str):
        tentativas = 3
        for i in range(tentativas):
            try:
                resultado = self._sistema.buscar(entry)
                self._fila_busca.put(("ok", resultado))
                return
            except Exception as e:
                if i < tentativas - 1:
                    sleep(2) 
                else:
                    self._fila_busca.put(("erro", e))

    # Verifica se a busca gerou resultados
    def _verificar_busca(self):
        try:
            resultado = self._fila_busca.get_nowait()
        except Empty:
            self.after(100, self._verificar_busca)
            return

        if resultado[0] == "ok":
            _, midias = resultado
            self._exibir_resultados(midias)
        else:
            _, erro = resultado
            print(f"Erro ao buscar mídias: {erro}")
            self._label_status.configure(text="Serviço temporariamente indisponível. Tente novamente.")

    # Exibe as mídias como cards em um scrollable frame    
    def _exibir_resultados(self, midias):
        if hasattr(self, "_frame_resultados"):
            self._frame_resultados.destroy()

        self._frame_resultados = ctk.CTkScrollableFrame(self, fg_color="transparent", height=640)
        self._frame_resultados.grid(row=1, column=0, columnspan=2, sticky="nsew")

        for widget in self._frame_resultados.winfo_children():
            widget.destroy()

        for j in range(0, 3):
            for i in range(0, 7):
                index = i + (j * 7)
                midia = midias[index] if index < len(midias) else None
                if midia:
                    card = CardMidia(self._frame_resultados, midia, comando=self._ao_clicar)
                    card.grid(row=j, column=i, padx=5, pady=5, sticky="n")

# Classe que cria um card no formato de exibição utilizado no painel direito, na busca e no painel de recomendações
class CardMidia(ctk.CTkFrame):
    def __init__(self, pai, midia, comando=None):
        super().__init__(pai, width=160, cursor="hand2")
        self._altura = 195
        self._largura = 130
        self._midia   = midia
        self._comando = comando
        self._img_ref = None
        self._fila_poster = Queue()
        self._construir()
        self._carregar_poster()

    # Constrói o card
    def _construir(self):
        self._label_poster = ctk.CTkLabel(self, text="", width=self._largura, height=self._altura, fg_color="#3a3a3a")
        self._label_poster.pack(padx=6, pady=(6, 2))

        ctk.CTkLabel(self, text=self._midia.get_titulo(), font=("Arial", 12, "bold"), wraplength=self._largura - 12, justify="center").pack(padx=6)

        rodape = ctk.CTkFrame(self, fg_color="transparent", width=self._largura)
        rodape.pack(padx=6, pady=(2, 6))

        ano = (self._midia.get_data_lancamento() or "")[:4]
        ctk.CTkLabel(rodape, text=ano, font=("Arial", 11), text_color="gray").pack(side="left", padx=(0, 10))

        nota = self._midia.get_avaliacoes()
        nota_texto = f"★ {nota:.1f}" if nota else ""
        ctk.CTkLabel(rodape, text=nota_texto, font=("Arial", 11), text_color="#f5c518").pack(side="right", padx=(10, 0))

        self._bind_clique(self)

    # Torna o card clicável
    def _bind_clique(self, widget):
        if self._comando:
            widget.bind("<Button-1>", lambda e: self._comando(self._midia))
            for filho in widget.winfo_children():
                self._bind_clique(filho)

    # Thread para carregar o poster
    def _carregar_poster(self):
        path = self._midia.get_poster_path()
        if not path:
            return
        thread = threading.Thread(target=self._worker_poster, args=(path,), daemon=True)
        thread.start()
        self.after(100, self._verificar_poster)

    # Worker que faz a busca do poster
    def _worker_poster(self, path):
        try:
            url = TMDB_IMAGE_BASE + path
            resposta = requests.get(url, timeout=5)
            resposta.raise_for_status()
            imagem = Image.open(BytesIO(resposta.content))
            imagem = imagem.resize((self._largura, self._altura))
            self._fila_poster.put(("ok", imagem))
        except Exception as e:
            self._fila_poster.put(("erro", e))

    # Verifica se o poster foi encontrado para exibição
    def _verificar_poster(self):
        try:
            status, resultado = self._fila_poster.get_nowait()
        except Empty:
            self.after(100, self._verificar_poster)
            return

        if status == "ok":
            self._aplicar_poster(resultado)

    # Posiciona o poster no card
    def _aplicar_poster(self, imagem):
        try:
            ctk_img = ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(self._largura, self._altura))
            self._img_ref = ctk_img
            self._label_poster.configure(image=ctk_img, text="")
        except Exception:
            pass    

# Classe que define as seções do painel direito, controlando a exibição de cards
class SecaoMidias(ctk.CTkFrame):
    def __init__(self, pai, titulo_secao: str):
        super().__init__(pai, fg_color="transparent")
        self._n = 7 # Quantida de cards na seção
        self._titulo_secao = titulo_secao
        self._frame_cards  = None
        self._construir()

    # Constrói a seção
    def _construir(self):
        ctk.CTkLabel(self, text=self._titulo_secao, font=("Arial", 15, "bold"), anchor="w").pack(fill="x", padx=30, pady=(10, 4))

        self._frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_cards.pack(fill="x", padx=10)

        for i in range(self._n):
            self._frame_cards.grid_columnconfigure(i, weight=1, uniform="card", minsize=130)

    # Método chamado pelas outras classes, passando a mídias para criação dos cards 
    def exibir(self, midias: list, comando=None):
        if not self._frame_cards or not self._frame_cards.winfo_exists():
            return 
        
        # Limpa a seção
        for widget in self._frame_cards.winfo_children():
            widget.destroy()

        # Verifica se há mídias (poderia ser uma lista vazia)
        if not midias:
            ctk.CTkLabel(self._frame_cards, text="Nenhuma mídia encontrada.", text_color="gray").grid(row=0, column=0, columnspan=self._n, pady=12)
            return

        # Cria e posiciona os cards lado a lado
        for i, midia in enumerate(midias[:self._n]):
            card = CardMidia(self._frame_cards, midia, comando=comando)
            card.grid(row=0, column=i, padx=2, pady=5, sticky="n")

# Página exibida quando um card é clicado (aplicável tanto para os cards do painel esquerdo quanto direito)
class PaginaMidia(ctk.CTkToplevel):
    # Difentemente das outras páginas, essa abre em toplevel, criando uma nova janela
    def __init__(self, pai, sistema: Sistema, midia: Midia):
        super().__init__(pai)
        self._largura = 200
        self._altura = 300
        self._sistema = sistema
        self._midia = self._sistema.detalhes_midia(midia) # Busca mais detalhes da mídia clicada
        self._callback_avaliacao = pai.esquerdo.atualizar
        self._img_ref = None
        self._fila_poster = Queue()

        self.title(midia.get_titulo())
        self.geometry("600x700+150+0")
        self.resizable(False, True)
        self.grab_set()

        self._avaliacao = self._sistema.get_avaliacao_usuario(midia.get_id())
        self._construir()
        self._carregar_poster()

    # Constrói a página
    def _construir(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._label_poster = ctk.CTkLabel(self, text="", width=self._largura, height=self._altura)
        self._label_poster.grid(row=0, column=0, padx=(16, 12), pady=16, sticky="n")

        # Painel de informações 
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
        info.grid_columnconfigure(0, weight=1)
        self._construir_info(info)

        # Rodapé: comentário e ações 
        self._frame_rodape = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_rodape.grid(row=1, column=0, columnspan=2, sticky="ew",padx=16, pady=(0, 16))
        self._frame_rodape.grid_columnconfigure(0, weight=1)
        self._construir_rodape()

    # Constrói as informações da mídia acessada
    def _construir_info(self, pai):
        linha = 0

        # Título
        ctk.CTkLabel(pai, text=self._midia.get_titulo(), font=("Arial", 18, "bold"), wraplength=380, justify="left", anchor="w").grid(row=linha, column=0, sticky="w", pady=(0, 4))
        linha += 1

        # Gêneros
        generos = ", ".join(self._midia.get_generos()) if self._midia.get_generos() else "—"
        ctk.CTkLabel(pai, text=generos, font=("Arial", 12), text_color="gray", wraplength=380, justify="left", anchor="w").grid(row=linha, column=0, sticky="w", pady=(0, 8))
        linha += 1

        # Resumo
        self._linha_dado(pai, linha, "Resumo", self._midia.get_descricao(), wrap=280)
        linha += 1

        # Dados específicos por tipo
        if isinstance(self._midia, Filme): # Caso seja um filme
            duracao = self._midia.get_duracao()
            duracao_fmt = f"{duracao // 60}h {duracao % 60}min" if duracao else "—"
            self._linha_dado(pai, linha, "Duração", duracao_fmt)
            linha += 1
            self._linha_dado(pai, linha, "Lançamento", self._midia.get_data_lancamento() or "—")
            linha += 1
            colecao = self._midia.get_colecao()
            if colecao:
                self._linha_dado(pai, linha, "Coleção", colecao)
                linha += 1

        elif isinstance(self._midia, Serie): # Caso seja uma série
            self._linha_dado(pai, linha, "Temporadas", str(self._midia.get_temporadas()))
            linha += 1
            self._linha_dado(pai, linha, "Episódios", str(self._midia.get_episodios()))
            linha += 1
            self._linha_dado(pai, linha, "Status", self._midia.get_status() or "—")
            linha += 1
            self._linha_dado(pai, linha, "Último episódio", str(self._midia.get_ano_final() or "—"))
            linha += 1

        # Nota TMDB / Nota do usuário
        if self._avaliacao:
            self._label_nota_usuario = ctk.CTkLabel(pai, text=f"Sua avaliação: ★ {self._avaliacao.get_nota():.1f}", font=("Arial", 14, "bold"), text_color="#f5c518", anchor="w")
            self._label_nota_usuario.grid(row=linha, column=0, sticky="w", pady=(12, 0))
        else:
            nota_tmdb = self._midia.get_avaliacoes()
            nota_tmdb_txt = f"★ {nota_tmdb:.1f}" if nota_tmdb else "—"
            self._linha_dado(pai, linha, "Nota TMDB", nota_tmdb_txt, cor_valor="#f5c518")
        linha += 1

        self._linha_acoes = linha  # guarda para posicionar botão/slider depois
        self._pai_info = pai       # guarda referência para _construir_modo_avaliacao
        self._construir_botao_acao(pai, linha)

    # Usado no método anterior para gerar as linhas exibidas
    def _linha_dado(self, pai, row, rotulo, valor, cor_valor=None, wrap=0):
        frame = ctk.CTkFrame(pai, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="w", pady=2)
        ctk.CTkLabel(frame, text=f"{rotulo}:", font=("Arial", 12, "bold"), anchor="w").pack(side="left", padx=(0, 6))
        ctk.CTkLabel(frame, text=valor, font=("Arial", 12), wraplength=wrap, text_color=cor_valor or "white", anchor="w").pack(side="left")

    # Exibe comentário existente ou vazio, reconstruído após salvar
    def _construir_rodape(self):
        for widget in self._frame_rodape.winfo_children():
            widget.destroy()

        if self._avaliacao and self._avaliacao.get_comentario():
            ctk.CTkLabel(self._frame_rodape, text=f'"{self._avaliacao.get_comentario()}"', font=("Arial", 12, "italic"), text_color="gray", wraplength=500, justify="center").grid(row=0, column=0, pady=(0, 4))

    # Gera um botão de acordo com a mídia já ter sido avaliada ou não
    def _construir_botao_acao(self, pai, linha):
        self._frame_acao = ctk.CTkFrame(pai, fg_color="transparent")
        self._frame_acao.grid(row=linha, column=0, sticky="w", pady=(16, 0))

        texto = "Editar avaliação" if self._avaliacao else "Avaliar"
        ctk.CTkButton(self._frame_acao,text=texto, width=140, command=self._ativar_modo_avaliacao).pack()

    # Destrói o botão e constrói slider e campo de comentário no mesmo lugar
    def _ativar_modo_avaliacao(self):
        for widget in self._frame_acao.winfo_children():
            widget.destroy()

        nota_inicial = self._avaliacao.get_nota() if self._avaliacao else 2.5

        # Slider de nota
        ctk.CTkLabel(self._frame_acao, text="Sua nota:", font=("Arial", 12, "bold")).pack(anchor="w")

        self._var_nota = ctk.DoubleVar(value=nota_inicial)

        frame_slider = ctk.CTkFrame(self._frame_acao, fg_color="transparent")
        frame_slider.pack(fill="x", pady=(2, 8))

        self._slider = ctk.CTkSlider(frame_slider, from_=0, to=10, number_of_steps=20, variable=self._var_nota, width=200, command=self._atualizar_label_nota)
        self._slider.pack(side="left")

        self._label_nota_slider = ctk.CTkLabel(frame_slider, text=f"★ {nota_inicial:.1f}", font=("Arial", 13, "bold"), text_color="#f5c518", width=50)
        self._label_nota_slider.pack(side="left", padx=(10, 0))

        # Campo de comentário no lugar do texto exibido
        for widget in self._frame_rodape.winfo_children():
            widget.destroy()

        comentario_inicial = self._avaliacao.get_comentario() if self._avaliacao else ""

        self._entry_comentario = ctk.CTkTextbox(self._frame_rodape, height=120, wrap="word")
        self._entry_comentario.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self._entry_comentario.insert("0.0", comentario_inicial)

        # Botões Salvar e Cancelar
        frame_btns = ctk.CTkFrame(self._frame_rodape, fg_color="transparent")
        frame_btns.grid(row=1, column=0)

        ctk.CTkButton(frame_btns, text="Salvar", width=100, command=self._salvar_avaliacao).pack(side="left", padx=(0, 8))

        ctk.CTkButton(frame_btns, text="Cancelar", width=100, fg_color="transparent", border_width=1, command=self._cancelar).pack(side="left")

    # Atualiza o label em tempo real
    def _atualizar_label_nota(self, valor):
        self._label_nota_slider.configure(text=f"★ {float(valor):.1f}")

    # Salva a avaliação, chamando o método de Sistema
    def _salvar_avaliacao(self):
        nota = round(self._var_nota.get(), 1)
        comentario = self._entry_comentario.get("0.0", "end").strip()

        sucesso = self._sistema.avaliar(self._midia, nota, comentario)

        if sucesso:
            # Recarrega a avaliação e reconstrói os painéis afetados
            self._avaliacao = self._sistema.get_avaliacao_usuario(self._midia.get_id())
            self._reconstruir_pos_avaliacao()
            if self._callback_avaliacao:
                self._callback_avaliacao()  # atualiza o painel esquerdo
        else:
            ctk.CTkLabel(self._frame_rodape, text="Erro ao salvar. Tente novamente.", text_color="red" ).grid(row=2, column=0)

    # Volta ao estado original sem salvar
    def _cancelar(self):
        self._frame_acao.destroy()
        self._construir_rodape()
        self._construir_botao_acao(self._pai_info, self._linha_acoes)

    # Atualiza a página para refletir a nova avaliação
    def _reconstruir_pos_avaliacao(self):
        self._frame_acao.destroy()
        if hasattr(self, "_label_nota_usuario"):
            self._label_nota_usuario.configure(text=f"Sua avaliação: ★ {self._avaliacao.get_nota():.1f}")
        self._construir_rodape()
        self._construir_botao_acao(self._pai_info, self._linha_acoes)

    # 4 métodos padrão para carregar poster em thread secundária
    def _carregar_poster(self):
        path = self._midia.get_poster_path()
        if not path:
            return
        thread = threading.Thread(target=self._worker_poster, args=(path,), daemon=True)
        thread.start()
        self.after(100, self._verificar_poster)

    def _worker_poster(self, path):
        try:
            url = TMDB_IMAGE_BASE + path
            resposta = requests.get(url, timeout=5)
            resposta.raise_for_status()
            imagem = Image.open(BytesIO(resposta.content))
            imagem = imagem.resize((self._largura, self._altura))
            self._fila_poster.put(("ok", imagem))
        except Exception as e:
            self._fila_poster.put(("erro", e))

    def _verificar_poster(self):
        try:
            status, resultado = self._fila_poster.get_nowait()
        except Empty:
            self.after(100, self._verificar_poster)
            return

        if status == "ok":
            self._aplicar_poster(resultado)

    def _aplicar_poster(self, imagem):
        try:
            ctk_img = ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(self._largura, self._altura))
            self._img_ref = ctk_img
            self._label_poster.configure(image=ctk_img, text="")
        except Exception:
            pass    

# Painel de recomendações, exibe cards de mídias recomendadas e uma breve justificativa das escolhas
class PainelRecomendacoes(ctk.CTkFrame):
    def __init__(self, pai, sistema : Sistema):
        super().__init__(pai)
        self._pai = pai
        self._sistema = sistema
        self._fila_recomendacoes = Queue()
        self._mensagem = None
        self._prompt = None
        self._construir()

    # Constrói o painel
    def _construir(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        cabecalho.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(cabecalho, text="Recomendações", font=("Arial", 15, "bold"), anchor="center").grid(row=0, column=0, sticky="w", padx=(30, 0))

        # Divide o painel em três frames, um para exibir os cards de mídia recomendados
        self._frame_resultados = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_resultados.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Outro para a mensagem retornada pelo LLM
        self._frame_mensagem = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_mensagem.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        # E um para a entrada de texto do usuário
        self._frame_chat = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_chat.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        self._entry_prompt = ctk.CTkEntry(self._frame_chat, placeholder_text="Que tipo de recomendação você quer hoje?", height=40, width=600)
        self._entry_prompt.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self._btn_prompt = ctk.CTkButton(self._frame_chat, text="↑", height=40, command=self._verifica_prompt)
        self._btn_prompt.pack(side="right")

        # Mostra o status atual da geração do painel
        self._label_status = ctk.CTkLabel(self._frame_resultados, text="Carregando...", text_color="gray")
        self._label_status.grid(row=0, column=0, columnspan=7, pady=20)

        self.after(100, self._carregar_recomendacoes)

    # Recomendações carregadas em threads secundárias para não travar enquanto aguarda resposta do LLM
    def _carregar_recomendacoes(self):
        for widget in self._frame_resultados.winfo_children():
            widget.destroy()

        self._label_status = ctk.CTkLabel(self._frame_resultados, text="Carregando...", text_color="gray")
        self._label_status.pack(expand=True, anchor="center")

        thread = threading.Thread(target=self._worker_recomendacoes, daemon=True)
        thread.start()
        self.after(100, self._verificar_recomendacoes)

    # Chama o método de Sistema que retorna as recomendações
    def _worker_recomendacoes(self):
        try:
            recomendacoes = self._sistema.descobrir(self._prompt)
            self._fila_recomendacoes.put(("ok", recomendacoes))
        except Exception as e:
            self._fila_recomendacoes.put(("erro", e))

    # Verifica o que foi retornado para a exibição
    def _verificar_recomendacoes(self):
        try:
            resultado = self._fila_recomendacoes.get_nowait()
        except Empty:
            self.after(100, self._verificar_recomendacoes)
            return

        if resultado[0] == "ok":
            _, sugestoes = resultado
            self._exibir_recomendacoes(sugestoes or [])
        else:
            _, erro = resultado
            print(f"Erro ao gerar recomendações: {erro}")
            self._exibir_erro()

    # Recebe as recomendações e monta a exibição
    def _exibir_recomendacoes(self, sugestoes):
        for widget in self._frame_resultados.winfo_children():
            widget.destroy()

        self._mensagem = sugestoes["mensagem"]
        recomendacoes = self._sistema.gerar_recomendacoes(sugestoes)

        if not recomendacoes:
            ctk.CTkLabel(self._frame_resultados, text="Nenhuma recomendação encontrada.", text_color="gray").grid(row=0, column=0, columnspan=7, pady=20)
            return

        frame_cards = ctk.CTkFrame(self._frame_resultados, fg_color="transparent")
        frame_cards.pack(anchor="center")

        # Cria os cards de mídia
        for index, midia in enumerate(recomendacoes):
            row = index // 7
            column = index % 7
            card = CardMidia(frame_cards, midia, comando=self._ao_clicar)
            card.grid(row=row, column=column, padx=5, pady=5, sticky="n")

        mensagem_llm = ctk.CTkLabel(self._frame_mensagem, text=self._mensagem, wraplength=800, font=("Georgia", 20), justify="center", text_color="#AAAAAA")
        mensagem_llm.pack(expand=True, anchor="center")

    # Exibe mensagem de erro
    def _exibir_erro(self):
        for widget in self._frame_resultados.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self._frame_resultados, text="Serviço temporariamente indisponível. Tente novamente.", text_color="gray",).grid(row=0, column=0, columnspan=7, pady=20)

    # Abre a página de mídia ao clicar no card
    def _ao_clicar(self, midia):
        PaginaMidia(self._pai, sistema=self._sistema, midia=midia)

    # Veirifica o input de prompt do usuário, enviado para o Sistema na geração de recomendações
    def _verifica_prompt(self):
        if not self._entry_prompt.get():
            return
        
        for widget in self._frame_mensagem.winfo_children():
            widget.destroy()

        self._prompt = self._entry_prompt.get()
        self._entry_prompt.delete(0, "end")
        self._btn_prompt.focus()
        self.after(10, lambda: self._entry_prompt._activate_placeholder())

        self._carregar_recomendacoes()