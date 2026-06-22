from services.tmdb import ClienteTMBD

class Sistema:
    def __init__ (self):
        self._cliente = ClienteTMBD()

    def buscar(self, keyword : str):
        try:
            response = self._cliente.buscar(keyword)
        except Exception as e:
            print(e)
            return
        filmes = ()
        series = ()
        pessoas = ()

        for resultado in response["results"]:
            match resultado["media_type"]:
                case "movie":
                    filmes.append(resultado)
                case "tv":
                    series.append(resultado)
                case "person":
                    pessoas.append(resultado)
                case _:
                    raise Exception("Erro: API retornou resultado de tipo (media_type) desconhecido")
                
    def descobrir(self):
        try:
            response = self._cliente.descobrir()
        except Exception as e:
            print(e)
            return
        
        pass