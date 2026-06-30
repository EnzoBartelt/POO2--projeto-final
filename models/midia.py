from models.avaliacao import Avaliacao

class Midia:
    def __init__ (self, tmdb_id : int, titulo : str, generos : list, descricao : str, avaliacoes : float, poster_path : str, data_lancamento : str):
        self._tmdb_id = tmdb_id                         # Identificador único (id)
        self._titulo = titulo                           # Título da obra (original_title)
        self._generos = generos                         # Gênero(s) (Drama, Suspense, Ação, Terror, etc) (genre_ids)
        self._descricao = descricao                     # Breve resumo/sinopse (overview)
        self._avaliacoes = avaliacoes                   # Avaliações registradas pelos usuários (vote_average)
        self._poster_path = poster_path                 # Endpoint para localização da imagem de poster (poster_path)
        self._data_lancamento = data_lancamento         # Data de lançamento para o público (release_date)

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_id(self):
        return self._tmdb_id

    def get_titulo(self):
        return self._titulo
    
    def get_generos(self):
        return self._generos
    
    def get_descricao(self):
        return self._descricao
    
    def get_avaliacoes(self):
        return self._avaliacoes
    
    def get_poster_path(self):
        return self._poster_path
    
    def get_data_lancamento(self):
        return self._data_lancamento
    
# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

        
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

# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def set_duracao(self, duracao : int):
        self._duracao = duracao

    def set_colecao(self, colecao : str):
        self._colecao = colecao

class Serie(Midia):
    def __init__ (self, tmdb_id : int, titulo : str, generos : list, descricao : str, avaliacoes : float, poster_path : str, data_lancamento : str, temporadas : int, episodios : int, ano_final : str, status : str):
        super().__init__(tmdb_id, titulo, generos, descricao, avaliacoes, poster_path, data_lancamento)
        self._temporadas = temporadas                        # Quantidade de temporadas (number_of_seasons)
        self._episodios = episodios                          # Quantidade de episódios (number_of_episodes)        
        self._ano_final = ano_final                          # Data do encerramento de exibição (último episódio) (last_air_date)
        self._status = status                                # Status da produção (Encerrada/Ativa) (status)
        
# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_temporadas(self):
        return self._temporadas
    
    def get_episodios(self):
        return self._episodios
    
    def get_ano_final(self):
        return self._ano_final
    
    def get_status(self):
        return self._status
    
# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def set_temporadas(self, temporadas : int):
        self._temporadas = temporadas

    def set_episodios(self, episodios : int):
        self._episodios = episodios

    def set_ano_final(self, ano_final : str):
        self._ano_final = ano_final

    def set_status(self, status : str):
        self._status = status