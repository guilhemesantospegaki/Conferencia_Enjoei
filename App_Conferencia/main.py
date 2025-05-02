from core import atualizador
atualizador.verificar_e_atualizar()  # Verifica antes de abrir o app

from PySide6.QtWidgets import QApplication
from ui.layout import ValidadorApp, SplashScreen
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    splash.start(ValidadorApp)
    sys.exit(app.exec())
