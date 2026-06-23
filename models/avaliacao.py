class Avaliacao:
    def __init__ (self, nota : float, comentario : str):
        self._nota = nota               # Nota dada pelo usuário
        self._comentario = comentario   # Comentário inserido pelo usuário

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_nota(self):
        return self._nota

    def get_comentario(self):
        return self._comentario

# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def set_nota(self, nota : float):
        self._nota = nota

    def set_comentario(self, comentario : str):
        self._comentario = comentario