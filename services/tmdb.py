import requests
import os

class ClienteTMBD:
    def __init__(self):
        self._base_url = "https://api.themoviedb.org/3"
        self._headers = {"Authorization" : f"Bearer {os.getenv('TMDB_API_KEY')}", "accept" : "application/json"}
        self._generos = None

    def buscar(self, keyword : str, page : int = 1):
        url = self._base_url + "/search/multi"
        params = {"query" : keyword, "language" : "pt-BR", "page" : page}
        response = requests.get(url, params=params, headers=self._headers)

        if response.status_code == 200:
            dados = response.json()
            return dados
        else:
            raise Exception(f"Erro: {response.status_code}")
    
    def generos(self):
        if self._generos:
            return self._generos
        url_filmes = self._base_url + "/genre/movie/list"
        url_series = self._base_url + "/genre/tv/list"
        params={"language": "pt-BR"}
        filmes = requests.get(url_filmes, params=params, headers=self._headers).json()
        series = requests.get(url_series, params=params, headers=self._headers).json()
        mapa = {}
        for g in filmes["genres"] + series["genres"]:
            mapa[g["id"]] = g["name"]
        self._generos = mapa
        return mapa

    def trending(self):
        url = self._base_url + "/trending/all/day"
        params = {"language" : "pt-BR"}
        response = requests.get(url, params=params, headers=self._headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro: {response.status_code}")
        
    def upcoming(self):
        url = self._base_url + "/movie/upcoming"
        params = {"language" : "pt-BR"}
        response = requests.get(url, params=params, headers=self._headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro: {response.status_code}")

    def detalhes_filme(self, id : int):
        url = self._base_url + f"/movie/{id}"
        params = {"language" : "pt-BR"}
        response = requests.get(url, params=params, headers=self._headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro: {response.status_code}")

    def detalhes_serie(self, id : int):
        url = self._base_url + f"/tv/{id}"
        params = {"language" : "pt-BR"}
        response = requests.get(url, params=params, headers=self._headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro: {response.status_code}")

    def encontrar(self, id: str):
        endpoint = f"/find/{id}"
        url = self._base_url + endpoint
        params = {"external_source": "imdb_id", "language": "pt-BR"}
        response = requests.get(url, params=params, headers=self._headers)

        if response.status_code != 200:
            raise Exception(f"Erro: {response.status_code}")

        return response.json()
