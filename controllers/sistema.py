import json
import re
from itertools import chain

from models.midia import Midia, Filme, Serie
from models.usuario import Usuario
from models.avaliacao import Avaliacao

from services.groq import ClienteGroq
from services.tmdb import ClienteTMBD
from data.repositorio import Repositorio


class Sistema:
    def __init__(self):
        self._cliente_tmdb = ClienteTMBD()
        self._cliente_groq = ClienteGroq()
        self._repositorio = Repositorio()
        self._usuario = None
        self._id_usuario = None

    def cadastrar(self, nome : str, email : str, senha : str):
        if not nome or not email or not senha:
            raise Exception("Todos os campos são obrigatórios.")
        if not validar_nome(nome):
            raise Exception("O nome de usuário não pode conter caracteres especiais.")
        if not validar_email(email):
            raise Exception("Insira um formato de email válido.")
        if not validar_senha(senha):
            raise Exception("Senha fraca")

        usuario = Usuario(nome, email, senha)
        self._repositorio.salvar_usuario(usuario)
        return True
    
    def logar(self, input : str, senha : str) -> bool:
        if not input or not senha:
            raise Exception("Preencha todos os campos para continuar")

        usuario = None
        id_usuario = None

        match classificar_entrada(input):
            case "email":
                usuario, id_usuario = self._repositorio.buscar_usuario_email(input)
            case "nome":
                usuario, id_usuario = self._repositorio.buscar_usuario_nome(input)
            case "invalido":
                raise Exception("Insira um nome de usuário ou email válido.")
            case _:
                raise Exception("Erro desconhecido")

        if usuario and id_usuario:
            if self._repositorio.validar_senha(senha, usuario.get_senha()):
                self._usuario = usuario
                self._id_usuario = id_usuario
                self.carregar_midias()
                print(f"Login efetuado com sucesso! Usuário {self._usuario.get_nome()} ativo.")
                return True
        else:
            return False
        
    def deslogar(self):
        self._usuario = None
        self._id_usuario = None

    # Popula filmes_vistos do usuário e carrega o histórico para a interface
    def carregar_midias(self):
        filmes_vistos = self._repositorio.buscar_avaliacoes(self._id_usuario)
        self._usuario.set_filmes_vistos(filmes_vistos)
        self._historico = self._repositorio.buscar_historico(self._id_usuario)
        return self._historico
    
    # Retorna a avaliação do usuário logado para uma mídia, ou None.
    def get_avaliacao_usuario(self, tmdb_id: int) -> Avaliacao | None:
        if not self._historico:
            return None
        dados = self._historico.get(tmdb_id)
        if isinstance(dados, dict):
            return dados.get("avaliacao")
        return dados

    # Cria ou atualiza avaliação, salva no banco e atualiza o histórico.
    def avaliar(self, midia: Midia, nota: float, comentario: str) -> bool:
        avaliacao = Avaliacao(nota, comentario)
        sucesso = self._repositorio.salvar_avaliacao(self._id_usuario, midia, avaliacao)
        if sucesso:
            # Atualiza filmes_vistos do usuário
            self._usuario.get_filmes_vistos()[midia.get_id()] = avaliacao
            # Atualiza histórico da UI
            if self._historico is None:
                self._historico = {}
            self._historico[midia.get_id()] = {"midia": midia, "avaliacao": avaliacao}
        return sucesso

    def trending(self):
        mapa_generos = self._cliente_tmdb.generos() 
        trending = self._cliente_tmdb.trending()
        midias = []

        try:
            for item in trending["results"][:7]:
                generos = [mapa_generos.get(gid, "") for gid in item.get("genre_ids", [])]

                if item["media_type"] == "movie":
                    midias.append(Filme(
                        item["id"], item["title"], generos,
                        item["overview"], item["vote_average"],
                        item["poster_path"], item["release_date"],
                        0, None
                    ))
                elif item["media_type"] == "tv":
                    midias.append(Serie(
                        item["id"], item["name"], generos,
                        item["overview"], item["vote_average"],
                        item["poster_path"], item["first_air_date"],
                        0, 0, None, item.get("status", "")
                    ))

            return midias
        
        except Exception as e:
            print(e)
            return None

    def upcoming(self):
        mapa_generos = self._cliente_tmdb.generos()
        dados = self._cliente_tmdb.upcoming()
        midias = []

        try:
            for item in dados["results"][:7]:
                generos = [mapa_generos.get(gid, "") for gid in item.get("genre_ids", [])]
                midias.append(Filme(
                    item["id"], item["title"], generos,
                    item.get("overview", ""), item.get("vote_average", 0),
                    item.get("poster_path", ""), item.get("release_date", ""),
                    0, None
                ))
            return midias
        
        except Exception as e:
            print(e)
            return []

    def buscar(self, keyword: str):
        try:
            response = self._cliente_tmdb.buscar(keyword)
        except Exception as e:
            print(e)
            return
        filmes = []
        series = []
        pessoas = []

        for resultado in response["results"]:
            match resultado["media_type"]:
                case "movie":
                    filmes.append(resultado)
                case "tv":
                    series.append(resultado)
                case "person":
                    pessoas.append(resultado)
                case _:
                    raise Exception(
                        "Erro: API retornou resultado de tipo (media_type) desconhecido"
                    )

    def descobrir(self):
        try:
            response = self._cliente_tmdb.descobrir()
        except Exception as e:
            print(e)
            return

        pass

    def detalhes_midia(self, midia : Midia) -> Midia:
        if isinstance(midia, Filme):
            response = self._cliente_tmdb.detalhes_filme(midia.get_id())
            midia.set_duracao(response["runtime"])
            midia.set_colecao(response["belongs_to_collection"]["name"])
            return midia
        elif isinstance(midia, Serie):
            response = self._cliente_tmdb.detalhes_serie(midia.get_id())
            midia.set_temporadas(response["number_of_seasons"])
            midia.set_episodios(response["number_of_episodes"])
            midia.set_ano_final(response["last_air_date"])
            midia.set_status(response["status"])
            return midia
        else:
            return midia

    def gerar_recomendacoes(self) -> list[Midia]:
        titles = [
            "Pluribus",
            "Arrival",
            "Star Wars",
        ]  # rascunho; acho q deveria receber outros dados, como parâmetros
        raw = self._cliente_groq.prompt(f"""
        Forneça até cinco recomendações de filmes ou séries de TV com base nas seguintes mídias: {", ".join(titles)}. \
        Responda com uma lista JSON serializada e minificada, contendo os IDs dos filmes ou séries na IMDB.
        """)
        response = json.loads(raw)
        recomendacoes: list[Midia] = []

        for id in response:
            midia = self.encontrar(id)
            recomendacoes.append(midia)

        return recomendacoes

# --------------------------------------------------------------------------------------------------------------------------------------------
#   FUNÇÕES AUXILIARES
# --------------------------------------------------------------------------------------------------------------------------------------------

def validar_nome(nome: str) -> bool:
    return bool(re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome))

def validar_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def validar_senha(senha: str) -> bool:
    if len(senha) < 8:
        return False
    if not re.search(r'[A-Z]', senha):  # maiúscula
        return False
    if not re.search(r'[a-z]', senha):  # minúscula
        return False
    if not re.search(r'[0-9]', senha):  # número
        return False
    if not re.search(r'[\W_]', senha):  # caractere especial
        return False
    return True

def classificar_entrada(texto: str) -> str:
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', texto):
        return "email"
    
    if re.match(r'^[A-Za-zÀ-ÿ\s]+$', texto):
        return "nome"

    return "invalido"