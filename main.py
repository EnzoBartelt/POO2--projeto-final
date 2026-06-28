from dotenv import load_dotenv

from views.app import App


def main():
    app = App()
    app.mainloop()

load_dotenv()
main()
