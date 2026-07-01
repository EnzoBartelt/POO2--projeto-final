import json
import re
from difflib import SequenceMatcher

from models.midia import Midia, Filme, Serie
from models.usuario import Usuario
from models.avaliacao import Avaliacao

from services.groq import ClienteGroq
from services.tmdb import ClienteTMBD
from data.repositorio import Repositorio

# Classe Sistema faz todo o controle e conexão da interface do usuário com os serviços, repositório e classes
class Sistema:
    def __init__(self):
        # Instanciação do repositório (conexão com banco de dados) e dos clientes (conexão com APIs)
        self._cliente_tmdb = ClienteTMBD()
        self._cliente_groq = ClienteGroq()
        self._repositorio = Repositorio()
        self._usuario = None
        self._id_usuario = None

    # Verifica as entradas e salva o novo usuário no banco de dados
    def cadastrar(self, nome : str, email : str, senha : str) -> bool:
        if not nome or not email or not senha:
            raise Exception("Todos os campos são obrigatórios.")
        if not validar_nome(nome):
            raise Exception("O nome de usuário não pode conter caracteres especiais.")
        if not validar_email(email):
            raise Exception("Insira um formato de email válido.")
        if not validar_senha(senha):
            raise Exception("Senha fraca")

        usuario = Usuario(nome, email, senha)
        self._repositorio.salvar_usuario(usuario)
        return True
    
    # Verifica as entradas e valida o login
    def logar(self, input : str, senha : str) -> bool:
        if not input or not senha:
            raise Exception("Preencha todos os campos para continuar")

        usuario = None
        id_usuario = None

        # Verifica se o usuário tentou entrar usando email ou nome de usuário e valida de acordo
        match classificar_entrada(input):
            case "email":
                usuario, id_usuario = self._repositorio.buscar_usuario_email(input)
            case "nome":
                usuario, id_usuario = self._repositorio.buscar_usuario_nome(input)
            case "invalido":
                raise Exception("Insira um nome de usuário ou email válido.")
            case _:
                raise Exception("Erro desconhecido")

        # Se encontrar o usuário valida a senha digitada
        if usuario and id_usuario:
            if self._repositorio.validar_senha(senha, usuario.get_senha()):
                # Define o usuário do sistema
                self._usuario = usuario
                self._id_usuario = id_usuario
                self.carregar_midias()
                print(f"Login efetuado com sucesso! Usuário {self._usuario.get_nome()} ativo.")
                return True
        else:
            return False
        
    # Desloga o usuário, definindo o usuário ativo como None
    def deslogar(self) -> None:
        self._usuario = None
        self._id_usuario = None

    # Popula filmes_vistos do usuário e carrega o histórico para a interface
    def carregar_midias(self) -> dict | None:
        filmes_vistos = self._repositorio.buscar_avaliacoes(self._id_usuario)
        self._usuario.set_filmes_vistos(filmes_vistos)
        self._historico = self._repositorio.buscar_historico(self._id_usuario)
        return self._historico
    
    # Retorna a avaliação do usuário logado para uma mídia, ou None.
    def get_avaliacao_usuario(self, tmdb_id: int) -> Avaliacao | None:
        if not self._historico:
            return None
        dados = self._historico.get(tmdb_id)
        if isinstance(dados, dict):
            return dados.get("avaliacao")
        return dados

    # Cria ou atualiza avaliação, salva no banco e atualiza o histórico.
    def avaliar(self, midia: Midia, nota: float, comentario: str) -> bool:
        avaliacao = Avaliacao(nota, comentario)
        sucesso = self._repositorio.salvar_avaliacao(self._id_usuario, midia, avaliacao)
        if sucesso:
            # Atualiza filmes_vistos do usuário
            self._usuario.get_filmes_vistos()[midia.get_id()] = avaliacao
            # Atualiza histórico da UI
            if self._historico is None:
                self._historico = {}
            self._historico[midia.get_id()] = {"midia": midia, "avaliacao": avaliacao}
        return sucesso

    # Chama endpoint /trending da API do TMDB, retornando uma lista de objetos do tipo Filme ou Serie
    def trending(self) -> list[Midia]:
        mapa_generos = self._cliente_tmdb.generos() 
        trending = self._cliente_tmdb.trending()
        midias = []

        try:
            for item in trending["results"][:7]:
                generos = [mapa_generos.get(gid, "") for gid in item.get("genre_ids", [])]

                if item["media_type"] == "movie":
                    midias.append(Filme(
                        item["id"], item["title"], generos,
                        item["overview"], item["vote_average"],
                        item["poster_path"], item["release_date"],
                        0, None
                    ))
                elif item["media_type"] == "tv":
                    midias.append(Serie(
                        item["id"], item["name"], generos,
                        item["overview"], item["vote_average"],
                        item["poster_path"], item["first_air_date"],
                        0, 0, None, item.get("status", "")
                    ))

            return midias
        
        except Exception as e:
            print(e)
            return None

    # Chama endpoint /upcoming da API do TMDB, retornando uma lista de objetos do tipo Filme (esse endpoint acessa apenas filmes)
    def upcoming(self) -> list[Midia]:
        mapa_generos = self._cliente_tmdb.generos()
        dados = self._cliente_tmdb.upcoming()
        midias = []

        try:
            for item in dados["results"][:7]:
                generos = [mapa_generos.get(gid, "") for gid in item.get("genre_ids", [])]
                midias.append(Filme(
                    item["id"], item["title"], generos,
                    item.get("overview", ""), item.get("vote_average", 0),
                    item.get("poster_path", ""), item.get("release_date", ""),
                    0, None
                ))
            return midias
        
        except Exception as e:
            print(e)
            return []

    # Chama endpoint /search/multi da API do TMDB, retornando uma lista de objetos do tipo Filme ou Serie, com base na palavra chave utilizad
    def buscar(self, keyword: str, page : int = 1) -> list[Midia]:
        try:
            response = self._cliente_tmdb.buscar(keyword, page)
        except Exception as e:
            print(e)
            return
        
        mapa_generos = self._cliente_tmdb.generos()
        midias = []

        for resultado in response["results"]:
            generos = [mapa_generos.get(gid, "") for gid in resultado.get("genre_ids", [])]

            match resultado["media_type"]:
                case "movie":
                    midias.append(Filme(
                        resultado["id"], 
                        resultado["title"], 
                        generos,
                        resultado["overview"], 
                        resultado["vote_average"],
                        resultado["poster_path"], 
                        resultado["release_date"],
                        0, None
                    ))
                case "tv":
                    midias.append(Serie(
                        resultado["id"], 
                        resultado["name"],
                        generos,
                        resultado["overview"], 
                        resultado["vote_average"],
                        resultado["poster_path"], 
                        resultado["first_air_date"],
                        0, 0, None, resultado.get("status", "")
                    ))
                case "person":
                    pass
                case _:
                    raise Exception(
                        "Erro: API retornou resultado de tipo (media_type) desconhecido"
                    )
                
        return midias

    # Realiza uma busca no histórico do usuário com base na similaridade de palavras 
    def buscar_historico(self, keyword: str) -> dict:
        if not self._historico or not keyword:
            return self._historico or {}
        
        keyword = keyword.lower().strip()

        limiar = 0.5 

        resultados = {tmdb_id: dados for tmdb_id, dados in self._historico.items() if similaridade(keyword, dados["midia"].get_titulo()) >= limiar}

        # Ordena do mais similar para o menos
        return dict(sorted(resultados.items(), key=lambda e: similaridade(keyword, e[1]["midia"].get_titulo()), reverse=True))

    # Gera sugestões utilizando a API do Groq
    def descobrir(self, prompt_usuario : str = None) -> dict:
        historico = getattr(self, "_historico", None) or self.carregar_midias()
        if not historico:
            return []

        melhores = sorted(
            self._historico.values(),
            key=lambda dados: dados["avaliacao"].get_nota(),
            reverse=True,
        )[:5]

        contexto = []
        for dados in melhores:
            midia = dados["midia"]
            avaliacao = dados["avaliacao"]
            tipo = "filme" if isinstance(midia, Filme) else "série"
            comentario = avaliacao.get_comentario()
            contexto.append(
                f"({midia.get_titulo()} | {tipo} | {avaliacao.get_nota():.1f} | {comentario} | {midia.get_generos()})"
            )

        prompt = f"""
            Você é um especialista em recomendações de filmes e séries.

            O usuário assistiu as seguintes mídias (título | tipo | nota | opinião | gêneros):
            {"\n".join(contexto)}

            Analise o histórico considerando:
            1. As notas dadas pelo usuário (peso maior para notas altas)
            2. Os gêneros mais assistidos e a média de avaliação por gênero
            3. A opinião popular (avaliação geral do público) sobre títulos semelhantes

            Pedido do usuário: "{prompt_usuario}"

            Leve o pedido do usuário como fator prioritário na seleção, mas combine com o perfil de gosto identificado acima. Ignorar se vazio.

            Recomende até 5 filmes ou séries que o usuário ainda NÃO assistiu (evite qualquer título já listado no histórico).

            Responda SOMENTE com JSON válido, sem texto extra, sem markdown, sem blocos de código, no formato:
            {{
            "mensagem": "Texto de até 500 palavras justificando as recomendações com base no perfil do usuário e no pedido feito. Direcionado ao usuário.",
            "recomendacoes": [
                {{"titulo": "titulo_do_filme", "tipo": "movie"}},
                {{"titulo": "titulo_da_serie", "tipo": "tv"}}
            ]
            }}

            Use "movie" para filmes e "tv" para séries.
        """

        try:
            response = self._cliente_groq.prompt(prompt)
            response = response.replace("```", "").replace("json", "")
            sugestoes = json.loads(response)
        except Exception as e:
            print(f"[GROQ] Erro ao gerar recomendações: {e}")
            return []

        return sugestoes
    
    # Gera lista de objetos do tipo Midia a partir do dicionário retornado pelo Groq
    def gerar_recomendacoes(self, sugestoes) -> list[Midia]:
        recomendacoes = []
        for sugestao in sugestoes["recomendacoes"]:
            try:
                for midia in self.buscar(sugestao["titulo"]):
                    if sugestao["tipo"] == "movie" and isinstance(midia, Filme):
                        recomendacoes.append(midia)
                        break
                    if sugestao["tipo"] == "tv" and isinstance(midia, Serie):
                        recomendacoes.append(midia)
                        break
            except Exception:
                pass

        return recomendacoes

    # Busca detalhes adicionais de determinada mídia, e complementa seus dados (são puxados da API incompletos para criação dos cards)
    def detalhes_midia(self, midia : Midia) -> Midia:
        if isinstance(midia, Filme):
            response = self._cliente_tmdb.detalhes_filme(midia.get_id())
            midia.set_duracao(response["runtime"])
            midia.set_colecao(response["belongs_to_collection"]["name"]) if response["belongs_to_collection"] else None
            return midia
        elif isinstance(midia, Serie):
            response = self._cliente_tmdb.detalhes_serie(midia.get_id())
            midia.set_temporadas(response["number_of_seasons"])
            midia.set_episodios(response["number_of_episodes"])
            midia.set_ano_final(response["last_air_date"])
            midia.set_status(response["status"])
            return midia
        else:
            return midia

# --------------------------------------------------------------------------------------------------------------------------------------------
#   FUNÇÕES AUXILIARES
# --------------------------------------------------------------------------------------------------------------------------------------------

# Evita carcteres especiais no nome
def validar_nome(nome: str) -> bool:
    return bool(re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome))

# Confere um formato de email básico
def validar_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

# Verifica os critérios de senha
def validar_senha(senha: str) -> bool:
    if len(senha) < 8:
        return False
    if not re.search(r'[A-Z]', senha):  # maiúscula
        return False
    if not re.search(r'[a-z]', senha):  # minúscula
        return False
    if not re.search(r'[0-9]', senha):  # número
        return False
    if not re.search(r'[\W_]', senha):  # caractere especial
        return False
    return True

# Verifica se uma entrada é email ou nome de usuário (com base nos critérios de validação)
def classificar_entrada(texto: str) -> str:
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', texto):
        return "email"
    
    if re.match(r'^[A-Za-zÀ-ÿ\s]+$', texto):
        return "nome"

    return "invalido"

# Verifica a semelhança entre duas strings (usado para busca no histórico)
def similaridade(keyword : str, titulo: str) -> float:
            titulo = titulo.lower()

            # Pontuação máxima entre: string inteira vs substring por palavra
            ratio_total = SequenceMatcher(None, keyword, titulo).ratio()
            ratio_palavras = max(
                SequenceMatcher(None, keyword, palavra).ratio()
                for palavra in titulo.split()
            )
            return max(ratio_total, ratio_palavras)
