Comandos DDL utilizados para criação do banco de dados. Para esse projeto, foi utilizado MySQL8, outros SGDBs podem ter alterções.

CREATE SCHEMA projeto_poo2;

USE projeto_poo2;

CREATE TABLE usuario (
	id_usuario INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    nome VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(60) NOT NULL
);

CREATE TABLE genero (
	id_genero INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    nome VARCHAR(60) UNIQUE
);

CREATE TABLE midia (
	id_tmdb INT NOT NULL PRIMARY KEY,
    titulo VARCHAR(255),
    descricao TEXT,
    poster_path VARCHAR(255),
    data_lancamento DATE
);

CREATE TABLE filme (
	id_tmdb INT NOT NULL PRIMARY KEY,
    duracao INT,
    colecao VARCHAR(255),
    FOREIGN KEY (id_tmdb) REFERENCES midia(id_tmdb)
		ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE serie (
	id_tmdb INT NOT NULL PRIMARY KEY,
    temporadas INT,
    episodios INT,
    data_final DATE,
    status VARCHAR(20),
    FOREIGN KEY (id_tmdb) REFERENCES midia(id_tmdb)
		ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE midia_genero (
    id_midia INT NOT NULL,
    id_genero INT NOT NULL,
    PRIMARY KEY (id_midia, id_genero),
    FOREIGN KEY (id_midia) REFERENCES midia(id_tmdb)
		ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (id_genero) REFERENCES genero(id_genero)
		ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE avaliacao (
	id_usuario INT NOT NULL,
    id_midia INT NOT NULL,
    nota DECIMAL(3,1) CHECK (0 <= nota AND nota <= 10),
    comentario TEXT,
    data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_midia),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
		ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (id_midia) REFERENCES midia(id_tmdb)
		ON UPDATE CASCADE ON DELETE CASCADE
);