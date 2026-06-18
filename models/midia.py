from models.avaliacao import Avaliacao

class Midia:
    def __init__ (self, titulo : str, genero : str, descricao : str, elenco : list, avaliacoes : list[Avaliacao]):
        self._titulo = titulo           # Título da obra
        self._genero = genero           # Gênero(s) (Drama, Suspense, Ação, Terror, etc)
        self._descricao = descricao     # Breve resumo/sinopse
        self._elenco = elenco           # Atores participantes
        self._avaliacoes = avaliacoes   # Avaliações registradas pelos usuários

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_titulo(self):
        return self._titulo
    
    def get_genero(self):
        return self._genero
    
    def get_descricao(self):
        return self._descricao
    
    def get_elenco(self):
        return self._elenco
    
    def get_avaliacoes(self):
        return self._avaliacoes
    
# --------------------------------------------------------------------------------------------------------------------------------------------
#   SETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def set_avaliacoes(self, avaliacoes : list[Avaliacao]):
        self._avaliacoes = avaliacoes

class Filme: 
    def __init__ (self, titulo : str, genero : str, descricao : str, elenco : list, avaliacoes : list[Avaliacao], duracao : int, ano_lancamento : int, colecao : str):
        super().__init__(self, titulo, genero, descricao, elenco, avaliacoes)
        self._duracao = duracao                  # Tempo em minutos da duração do filme
        self._ano_lancamento = ano_lancamento    # Ano de lançamento para o público
        self._colecao = colecao                  # Coleção ("Universo Cinematográfico") a que pertence (Ex: Star Wars, Harry Potter, Marvel, etc)

# --------------------------------------------------------------------------------------------------------------------------------------------
#   GETTERS
# --------------------------------------------------------------------------------------------------------------------------------------------

    def get_duracao(self):
        return self._duracao
    
    def get_ano_lancamento(self):
        return self._ano_lancamento
    
    def get_colecao(self):
        return self._colecao

class Serie:
    def __init__ (self, titulo : str, genero : str, descricao : str, elenco : list, avaliacoes : list[Avaliacao], temporadas : int, episodios : int, ano_lancamento : int, ano_final : int, avaliacao_episodios, avaliacao_temporadas):
        super().__init__(self, titulo, genero, descricao, elenco, avaliacoes)
        self._temporadas = temporadas                        # Quantidade de temporadas
        self._episodis = episodios                           # Quantidade de episódios
        self._ano_lancamento = ano_lancamento                # Ano de lançamento para o público
        self._ano_final = ano_final                          # Ano do encerramento de exibição (último episódio)
        self._avaliacao_episodios = avaliacao_episodios      # Avalição individual de cada episódio
        self._avaliacao_temporadas = avaliacao_temporadas    # Avaliação de cada temporada

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