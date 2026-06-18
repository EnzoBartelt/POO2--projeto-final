from models.usuario import Usuario

class Recomendacao:
    def __init__ (self, usuario : Usuario, comentario : str):
        self._usuario = usuario           # Usuário a qual essa recomendação pertence
        self._comentario = comentario     # Comentário do usuário quanto à recomendação (imput para LLM: instruções, pedidos, etc)

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_usuario(self):
        return self._usuario
    
    def get_comentario(self):
        return self._comentario

# --------------------------------------------------------------------------------------------------------------------------------------------
#   RECOMENDAR: Gera uma recomendação com base nas informações do usuário, e o comentário do usuário para o LLM
# --------------------------------------------------------------------------------------------------------------------------------------------

    def recomendar(self):
        pass