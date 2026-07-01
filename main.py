from dotenv import load_dotenv

from views.app import App

def main():
    app = App()
    app.mainloop()

load_dotenv() # Carrega as variáveis do arquivo .env e disponibiliza para a aplicação
main()
