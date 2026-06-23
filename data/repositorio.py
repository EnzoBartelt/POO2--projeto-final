import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from datetime import datetime
 
from models.avaliacao import Avaliacao
from models.midia import Midia, Filme, Serie
from models.usuario import Usuario


class Repositorio:
    def __init__ (self):
        self._conexao = None
        self._conectar()

    def _conectar(self):
        try:
            self._conexao = mysql.connector.connect(
                host = os.getenv('DB_HOST', "localhost"),
                port = int(os.getenv('DB_PORT', 3306)),
                user = os.getenv('DB_USER'),
                password = os.getenv('DB_PASSWORD'),
                database = os.getenv('DB_DATABSE', "projeto_poo2")
            )
            print("[DB] Conexão com banco de dados estabelecida com sucesso!")
        except Exception as e:
            print(f"[DB] Erro ao conectar: {e}")

    def fechar(self):
        if self._conexao and self._conexao.is_connected():
            self._conexao.close()
            print("[DB] Conexão encerrada.")

    def _cursor(self):
        if not self._conexao.is_connected():
            self._conectar()
        return self._conexao.cursor(dictionary=True)


    def salvar_usuario(self, usuario : Usuario):
        senha_hash = bcrypt.hashpw(
            usuario.get_senha().encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        sql = """
            INSERT INTO usuario (nome, email, senha)
            VALUES (%s, %s, %s)
            """
        
        try:
            cursor = self._cursor()
            cursor.execute(sql, (usuario.get_nome(), usuario.get_email(), senha_hash))
            self._conexao.commit()
            return True
        except Exception as e:
            print(f"[DB] Erro ao salvar usuário: {e}")
            return False
        finally:
            cursor.close()

    def buscar_usuario_email(self, email : str):
        sql = """
            SELECT * FROM usuario WHERE email = %s
            """

        try:
            cursor = self._cursor()
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            if user:
                return Usuario(user["nome"], user["email"], user["senha"]), user["id_usuario"]
            return None, None
        except Exception as e:
            print(f"[DB] Erro ao realizar busca: {e}")
            return None, None
        finally:
            cursor.close()

    def buscar_usuario_nome(self, nome : str):
        sql = """
            SELECT * FROM usuario WHERE nome = %s
            """
        
        try:
            cursor = self._cursor()
            cursor.execute(sql, (nome,))
            user = cursor.fetchone()
            if user:
                return Usuario(user["nome"], user["email"], user["senha"]), user["id_usuario"]
            return None, None
        except Exception as e:
            print(f"[DB] Erro ao realizar busca: {e}")
            return None, None
        finally:
            cursor.close()

    def validar_senha(self, input_senha : str, senha_hash : str):
        return bcrypt.checkpw(input_senha.encode('utf-8'), senha_hash.encode('utf-8'))
    

    def salvar_midia(self, midia : Midia):
        sql_midia = """
                INSERT IGNORE INTO midia (id_tmdb, titulo, descricao, poster_path, data_lancamento)
                VALUES (%s, %s, %s, %s, %s)
                """
        
        try:
            cursor = self._cursor()
            cursor.execute(sql_midia,(
                midia.get_id(),
                midia.get_titulo(),
                midia.get_descricao(),
                midia.get_poster_path(),
                midia.get_data_lancamento()
            ))

            if isinstance(midia, Filme):
                sql_tipo = """
                        INSERT IGNORE INTO filme (id_tmdb, duracao, colecao)
                        VALUES (%s, %s, %s)
                        """
                
                cursor.execute(sql_tipo, (
                    midia.get_id(),
                    midia.get_duracao(),
                    midia.get_colecao()
                ))
            
            elif isinstance(midia, Serie):
                sql_tipo = """
                        INSERT IGNORE INTO serie (id_tmdb, temporadas, episodios, data_final, status)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                
                cursor.execute(sql_tipo, (
                    midia.get_id(),
                    midia.get_temporadas(),
                    midia.get_episodios(),
                    midia.get_ano_final(),
                    midia.get_status()
                ))

            self._salvar_generos(cursor, midia)
            self._conexao.commit()
            return True
        
        except Exception as e:
            self._conexao.rollback()
            print(f"[DB] Erro ao salvar mídia: {e}")
            return False
        finally:
            cursor.close()

    def _salvar_generos(self, cursor, midia : Midia):
        for genero in midia.get_generos():
            cursor.execute("INSERT IGNORE INTO genero (nome) VALUES (%s)", (genero,))

            cursor.execute("SELECT id_genero FROM genero WHERE nome = %s", (genero,))

            alvo = cursor.fetchone()
            if alvo:
                cursor.execute("INSERT IGNORE INTO midia_genero (id_midia, id_geneto) VALUES (%s, %s)",
                               (midia.get_id(), alvo["id_genero"])
                            )
                
    def midia_existe(self, tmdb_id: int):
        try:
            cursor = self._cursor()
            cursor.execute("SELECT * FROM midia WHERE id_tmdb = %s", (tmdb_id,))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"[DB] Erro ao verificar mídia: {e}")
            return False
        finally:
            cursor.close()

    def salvar_avaliacao(self, usuario : Usuario, id_usuario : int, midia : Midia, avaliacao : Avaliacao):
        if not self.midia_existe(midia.get_id()):
            self.salvar_midia(midia)

        sql = """
            INSERT INTO avaliacao (id_usuario, id_midia, nota, comentario)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nota = VALUES(nota),
                comentario = VALUES(comentario)
            """
        
        try:
            cursor = self._cursor()
            cursor.execute(sql, (
                id_usuario,
                midia.get_id(),
                avaliacao.get_nota(),
                avaliacao.get_comentario()
            ))
            
            self._conexao.commit()
            return True
        
        except Exception as e:
            self._conexao.rollback()
            print(f"[DB] Erro ao salvar avaliação: {e}")
            return False
        
        finally:
            cursor.close()

    def buscar_avaliacoes(self, id_usuario : int):
        sql = """
            SELECT a.id_midia, a.nota, a.comentario, m.titulo FROM avaliacao a
            JOIN midia m ON m.id_tmdb = a.id_midia
            WHERE a.id_usuario = %s
            """
        
        try:
            cursor = self._cursor()
            cursor.execute(sql, (id_usuario,))

            rows = cursor.fetchall()
            resultado = {}

            for row in rows:
                av = Avaliacao(row["nota"], row["comentario"])
                resultado[row["id_midia"]] = av

            return resultado
        
        except Exception as e:
            print(f"[DB] Erro ao carregar avaliações: {e}")
            return None
        
        finally:
            cursor.close()

    def deletar_avaliacao(self, id_usuario : int, tmdb_id : int):
        sql = "DELETE FROM avaliacao WHERE id_usuario = %s AND id_midia = %s"

        try:
            cursor = self._cursor()
            cursor.execute(sql, (id_usuario, tmdb_id))
            self._conexao.commit()

            return cursor.rowcount > 0  
        
        except Error as e:
            self._conexao.rollback()
            print(f"[DB] Erro ao deletar avaliação: {e}")
            return False
        
        finally:
            cursor.close()