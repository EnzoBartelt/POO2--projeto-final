import json
import re
from itertools import chain

from models.midia import Midia, Filme, Serie
from models.usuario import Usuario

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
                print(f"Login efetuado com sucesso! Usuário {self._usuario.get_nome()} ativo.")
                return True
        else:
            return False
        
    def deslogar(self):
        self._usuario = None
        self._id_usuario = None

    def carregar_midias(self):
        pass

    def trending(self):
        midias = []

        try:
            trending = self._cliente_tmdb.trending()
            for midia in trending["results"]:
                generos = []

                if midia["media_type"] == "movie":
                    filme = self._cliente_tmdb.detalhes_filme(midia["id"])

                    for g in filme["genres"]:
                        generos.append(g["name"])

                    midias.append(Filme(
                        filme["id"], 
                        filme["original_title"], 
                        generos,
                        filme["overview"], 
                        filme["vote_average"], 
                        filme["poster_path"],
                        filme["release_date"],
                        filme["runtime"],
                        filme["belongs_to_collection"]["name"] if filme["belongs_to_collection"] else None
                    ))
                elif midia["media_type"] == "tv":
                    serie = self._cliente_tmdb.detalhes_serie(midia["id"])

                    for g in serie["genres"]:
                        generos.append(g["name"])

                    midias.append(Serie(
                        serie["id"],
                        serie["original_name"],
                        generos,
                        serie["overview"],
                        serie["vote_average"],
                        serie["poster_path"],
                        serie["first_air_date"],
                        serie["number_of_seasons"],
                        serie["number_of_episodes"],
                        serie["last_air_date"],
                        serie["status"]
                    ))

            return midias
        
        except Exception as e:
            print(e)
            return None

    def upcoming(self):
        midias = []

        try:
            upcoming = self._cliente_tmdb.upcoming()
            for midia in upcoming["results"]:
                generos = []

                filme = self._cliente_tmdb.detalhes_filme(midia["id"])

                for g in filme["genres"]:
                    generos.append(g["name"])

                midias.append(Filme(
                    filme["id"], 
                    filme["original_title"], 
                    generos,
                    filme["overview"], 
                    filme["vote_average"], 
                    filme["poster_path"],
                    filme["release_date"],
                    filme["runtime"],
                    filme["belongs_to_collection"]["name"] if filme["belongs_to_collection"] else None
                ))

            return midias
        
        except Exception as e:
            print(e)
            return None

    def buscar(self, keyword: str):
        try:
            response = self._cliente_tmdb.buscar(keyword)
        except Exception as e:
            print(e)
            return
        filmes = ()
        series = ()
        pessoas = ()

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

    def encontrar(self, id: str) -> Midia:
        response = self._cliente_tmdb.encontrar(id)
        result = next(chain(response["movie_results"], response["tv_results"]))

        if result["media_type"] == "movie":
            return Filme(
                result["id"],
                result["title"],
                # result["genres"],
                [],
                result["overview"],
                result["vote_average"],
                result["poster_path"],
                result["release_date"],
                # result["runtime"],
                0,
                # result["belongs_to_collection"]["name"],
                "",
            )
        elif result["media_type"] == "tv":
            return Serie(
                result["id"],
                result["name"],
                # result["genres"],
                [],
                result["overview"],
                result["vote_average"],
                result["poster_path"],
                result["first_air_date"],
                # result["number_of_seasons"],
                1,
                # result["number_of_episodes"],
                1,
                # result["last_air_date"],
                1,
                # result["episode_run_time"],
                1,
                # result["status"],
                "",
            )
        else:
            raise Exception(
                "Erro: API retornou resultado de tipo (media_type) desconhecido"
            )

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