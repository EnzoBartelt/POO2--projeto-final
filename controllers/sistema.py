import json
from itertools import chain
from models.midia import Midia, Filme, Serie
from services.groq import ClienteGroq
from services.tmdb import ClienteTMBD


class Sistema:
    def __init__(self):
        self._cliente_tmdb = ClienteTMBD()
        self._cliente_groq = ClienteGroq()

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
