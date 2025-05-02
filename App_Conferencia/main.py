from PySide6.QtWidgets import QApplication
from ui.layout import ValidadorApp, SplashScreen
from core import atualizador
import sys
import threading

def atualizar_app():
    atualizador.verificar_e_atualizar()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Rodando a verificação de atualização em um thread separado
    update_thread = threading.Thread(target=atualizar_app)
    update_thread.start()

    splash = SplashScreen()
    splash.show()
    splash.start(ValidadorApp)

    sys.exit(app.exec())
