from models.avaliacao import Avaliacao
from models.midia import *

class Usuario:
    def __init__ (self, nome : str, email : str, senha : str, filmes_vistos : dict[Midia, Avaliacao]):
        self._nome = nome               # nome de usuário 
        self._email = email             # email do usuário
        self._senha = senha             # senha do usuário
        self._filmes = filmes_vistos    # dicionário com as mídias assitidas pelo usuário e suas respectivas avaliações

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_nome(self):
        return self._nome
    
    def get_email(self):
        return self._email
    
    def get_senha(self):
        return self._senha
    
    def get_filmes_vistos(self):
        return self._filmes
    
# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------
    
    def set_nome(self, nome : str):
        self._nome = nome
    
    def set_email(self, email : str):
        self._email = email

    def set_senha(self, senha : str):
        self._senha = senha

    def set_filmes_vistos(self, filmes_vistos : dict[Midia : Avaliacao]):
        self._filmes = filmes_vistos