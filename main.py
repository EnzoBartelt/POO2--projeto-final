import json
from dotenv import load_dotenv

from data.repositorio import Repositorio
from controllers.sistema import Sistema
from services.tmdb import ClienteTMBD
from views.app import App


def main():
    # cliente = ClienteTMBD()
    
    sistema = Sistema()
    App(sistema)

load_dotenv()
main()
