from models.avaliacao import Avaliacao

class Midia:
    def __init__ (self, tmdb_id : int, titulo : str, generos : list, descricao : str, avaliacoes : float, poster_path : str, data_lancamento : str):
        self._tmdb_id = tmdb_id
        self._titulo = titulo           # Título da obra (original_title)
        self._generos = generos           # Gênero(s) (Drama, Suspense, Ação, Terror, etc) (genres)
        self._descricao = descricao     # Breve resumo/sinopse (overview)
        self._avaliacoes = avaliacoes   # Avaliações registradas pelos usuários (vote_average)
        self._poster_path = poster_path
        self._data_lancamento = data_lancamento

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_titulo(self):
        return self._titulo
    
    def get_genero(self):
        return self._genero
    
    def get_descricao(self):
        return self._descricao
    
    def get_avaliacoes(self):
        return self._avaliacoes
    
# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------
'''
    def set_avaliacoes(self, avaliacoes : list[Avaliacao]):
        self._avaliacoes = avaliacoes
'''
        
class Filme(Midia): 
    def __init__ (self, tmdb_id : int, titulo : str, generos : list, descricao : str, avaliacoes : float, poster_path : str, data_lancamento : str, duracao : int, colecao : str):
        super().__init__(tmdb_id, titulo, generos, descricao, avaliacoes, poster_path, data_lancamento)
        self._duracao = duracao                  # Tempo em minutos da duração do filme (runtime)
        self._colecao = colecao                  # Coleção ("Universo Cinematográfico") a que pertence (Ex: Star Wars, Harry Potter, Marvel, etc) (belongs_to_collection["name"])

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_duracao(self):
        return self._duracao
    
    def get_colecao(self):
        return self._colecao

class Serie(Midia):
    def __init__ (self, tmdb_id : int, titulo : str, generos : list, descricao : str, avaliacoes : float, poster_path : str, data_lancamento : str, temporadas : int, episodios : int, ano_final : int, avaliacao_temporadas, status : str):
        super().__init__(tmdb_id, titulo, generos, descricao, avaliacoes, poster_path, data_lancamento)
        self._temporadas = temporadas                        # Quantidade de temporadas (number_of_seasons)
        self._episodios = episodios                          # Quantidade de episódios (number_of_episodes)
        self._ano_final = ano_final                          # Ano do encerramento de exibição (último episódio) (last_air_date)
        self._avaliacao_temporadas = avaliacao_temporadas    # Avaliação de cada temporada
        self._status = status                                # Status da produção (Encerrada/Ativa) (status)
# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_temporadas(self):
        return self._temporadas
    
    def get_episodios(self):
        return self._episodios
    
    def get_ano_lancamento(self):
        return self._ano_lancamento
    
    def get_ano_final(self):
        return self._ano_final
    
    def get_avaliacao_episodios(self):
        return self._avaliacao_episodios
    
    def get_avaliacao_temporadas(self):
        return self._avaliacao_temporadas

# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def set_avaliacao_episodios(self, avaliacao_episodios):
        pass

    def set_avaliacao_temporadas(self, avaliacao_temporadas):
        pass