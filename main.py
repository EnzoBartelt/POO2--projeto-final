from services.tmdb import ClienteTMBD

def main():
    cliente = ClienteTMBD()

    dados = cliente.buscar("Star Wars")

    for resultado in dados["results"]:
        print(resultado)

main()