import json
from dotenv import load_dotenv

from controllers.sistema import Sistema
from services.tmdb import ClienteTMBD
from views.app import App


def main():
    cliente = ClienteTMBD()

    # dados = cliente.buscar("Star Wars")

    # for resultado in dados["results"]:
    #     print(resultado)

    sistema = Sistema()
    App(sistema)


load_dotenv()
main()
