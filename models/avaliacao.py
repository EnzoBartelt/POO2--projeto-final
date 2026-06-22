from models.midia import Midia
from datetime import datetime

class Avaliacao:
    def __init__ (self, nota : float, comentario : str, data : datetime):
        self._nota = nota               # Nota dada pelo usuário
        self._comentario = comentario   # Comentário inserido pelo usuário
        self._data = data               # Data da avaliação

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_midia(self):
        return self._midia
    
    def get_nota(self):
        return self._nota

    def get_comentario(self):
        return self._comentario
    
    def get_data(self):
        return self._data

# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def set_nota(self, nota : float):
        self._nota = nota

    def set_comentario(self, comentario : str):
        self._comentario = comentario

    def set_data(self, data : datetime):
        self._data = data