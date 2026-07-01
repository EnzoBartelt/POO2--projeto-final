# 🎬 Plataforma de Recomendação de Filmes e Séries

> Projeto final da disciplina de **Programação Orientada a Objetos II**

---

## Sobre o projeto

O projeto é uma aplicação desktop desenvolvida em Python que permite ao usuário registrar filmes e séries assistidos, atribuir avaliações e receber recomendações personalizadas geradas por inteligência artificial.

O catálogo de mídias é alimentado pela API gratuita do **The Movie Database (TMDB)**, que fornece endpoints de descoberta e busca específica, garantindo uma experiência rica e atualizada. O mecanismo de recomendação utiliza a API do **Groq** — um serviço de LLM com camada gratuita — que analisa o histórico do usuário levando em conta:

- As mídias com maiores notas atribuídas
- Os gêneros mais assistidos
- As avaliações gerais do público
- Um prompt personalizado fornecido pelo próprio usuário

---

## Pré-requisitos

Antes de executar a aplicação, certifique-se de ter instalado:

- Python 3.10 ou superior
- MySQL 8.0
- As dependências listadas em `requirements.txt`

```bash
pip install -r requirements.txt
```

---

## Como executar

### 1. Banco de dados

Crie o banco de dados MySQL com as tabelas necessárias. O código DDL completo está disponível em:

```
data/README.md
```

### 2. Chaves de API

Obtenha chaves de API válidas nos seguintes serviços:

| Serviço | Link |
|--------|------|
| TMDB | https://www.themoviedb.org/settings/api |
| Groq | https://console.groq.com |

### 3. Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com base no modelo disponível em `.env.example`, preenchendo as credenciais do banco de dados e as chaves de API obtidas.

### 4. Inicialização

```bash
python main.py
```

---

## Estrutura do projeto

O projeto segue uma arquitetura em camadas inspirada no padrão **MVC**, separando claramente as responsabilidades de cada módulo.

```
projeto/
├── controllers/
│   └── sistema.py
├── data/
│   ├── README.md
│   └── repositorio.py
├── models/
│   ├── avaliacao.py
│   ├── midia.py
│   └── usuario.py
├── services/
│   ├── groq.py
│   └── tmdb.py
├── views/
│   └── app.py
├── .env
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── UML.mdj
```

---

### `controllers/`

Camada responsável por **orquestrar a lógica de negócio**, intermediando as requisições da interface com os modelos e serviços.

#### `sistema.py`
Classe central da aplicação. Expõe os métodos utilizados pela camada de visão, como autenticação de usuários, carregamento do histórico, busca no catálogo, geração de recomendações e persistência de avaliações. É o único ponto de contato entre a interface gráfica e o restante do sistema.

---

### `data/`

Camada de **acesso e persistência de dados**.

#### `repositorio.py`
Responsável por toda a comunicação com o banco de dados MySQL. Contém os métodos de consulta, inserção e atualização utilizados pelo sistema, como busca de usuários, registro de mídias assistidas e salvamento de avaliações.

#### `README.md`
Contém o script DDL completo para criação das tabelas no MySQL 8. Deve ser executado antes da primeira inicialização da aplicação.

---

### `models/`

Camada de **representação dos dados** do domínio da aplicação. Cada arquivo define uma classe que encapsula os atributos e comportamentos de uma entidade do sistema.

#### `midia.py`
Define a classe `Midia`, e suas subclasses `Filme` e `Serie`, representando uma produção audiovisual com atributos como título, ano de lançamento, gêneros, nota geral e caminho do poster. As subclasses contém informações adicionais, levando em conta o tipo da obra.

#### `avaliacao.py`
Representa a avaliação feita por um usuário sobre uma mídia específica, encapsulando a nota atribuída e a relação entre usuário e mídia avaliada.

#### `usuario.py`
Modela o usuário da aplicação, com seus dados de identificação e métodos relacionados ao seu perfil.

---

### `services/`

Camada de **integração com serviços externos** via API. Isola toda a comunicação com o mundo externo, facilitando manutenção e substituição de provedores.

#### `tmdb.py`
Realiza requisições à API do The Movie Database. Responsável por buscar filmes e séries por nome, listar produções em destaque e obter detalhes como poster, sinopse, elenco e avaliação geral do público.

#### `groq.py`
Integra a API do Groq para geração de recomendações via LLM. Monta o prompt com base no histórico do usuário e no pedido personalizado, envia à API e interpreta a resposta retornando as sugestões de mídias.

---

### `views/`

Camada de **interface gráfica**, construída com [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

#### `app.py`
Contém todas as classes de interface da aplicação, organizadas em telas e painéis:

| Classe | Responsabilidade |
|--------|-----------------|
| `App` | Janela principal; gerencia a navegação entre telas |
| `TelaLogin` | Formulário de login e cadastro de novos usuários |
| `TelaPrincipal` | Layout principal pós-login com hotbar, painel esquerdo e painel direito |
| `PainelEsquerdo` | Exibe o histórico de mídias assistidas e campo de busca |
| `PainelDireito` | Área de conteúdo principal; exibe resultados de busca ou detalhes |
| `PainelRecomendacoes` | Painel de recomendações com entrada de prompt e exibição dos cards |
| `PaginaMidia` | Tela de detalhes de uma mídia, com poster, sinopse e opção de avaliação |

---

### Arquivos raiz

| Arquivo | Descrição |
|--------|-----------|
| `main.py` | Ponto de entrada da aplicação; instancia e inicia a classe `App` |
| `requirements.txt` | Lista de dependências Python do projeto |
| `.env.example` | Modelo do arquivo de variáveis de ambiente com os campos necessários |
| `.gitignore` | Arquivos e pastas ignorados pelo controle de versão |
| `UML.png` | Diagrama UML do projeto |