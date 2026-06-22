import requests
import os
from dotenv import load_dotenv

load_dotenv()

class ClienteTMBD:
    def __init__(self):
        self._base_url = "https://api.themoviedb.org/3"
        self._headers = {"Authorization" : f"Bearer {os.getenv('TMDB_API_KEY')}", "accept" : "application/json"}

    def buscar(self, keyword : str):
        endpoint = "/search/multi"
        url = self._base_url + endpoint
        params = {"query" : keyword, "language" : "pt-BR"}
        response = requests.get(url, params=params, headers=self._headers)

        if response.status_code == 200:
            dados = response.json()
            return dados
        else:
            raise Exception(f"Erro: {response.status_code}")
        
    def descobrir(self):
        endpoint = "/discover/movies"
        url = self._base_url + endpoint
        response = requests.get(url)

        if response.status_code == 200:
            return response.json
        else:
            raise Exception(f"Erro: {response.status_code}")