from PySide6.QtWidgets import QApplication
from ui.layout import ValidadorApp, SplashScreen # Certifique-se de importar corretamente a classe do layout
from core import atualizador
import sys

atualizador.verificar_e_atualizar()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    splash.start(ValidadorApp)
    sys.exit(app.exec())