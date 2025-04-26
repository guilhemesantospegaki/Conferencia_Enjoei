from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                                 QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtGui import QIcon, QFont, QColor, QPalette
from PySide6.QtCore import Qt, QSize
import sys
import pandas as pd
import re

# --- Dados iniciais ---
csv_path = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/refs/heads/main/Db_Pacotes_Enjoei.csv"
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()
df = df.applymap(lambda x: str(x).strip())

regex_pug = re.compile(r"^PUG\d{8}(CAM|BIR|GRU|FRC|RJO|GYN|JOI|CWB|MGA|DIV|CTG|PCD)$")

# --- Variáveis globais ---
pacotes_bipados = set()
ultimo_codigo = None
contador_validos = 0
pug_atual = None
pug_contagem = {}
ordem_por_pug = {}
linhas_destacadas = {}
estado = "aguardando_pug"

class SenhaDialog(QDialog):
    def __init__(self, mensagem):
        super().__init__()
        self.setWindowTitle("")
        self.setFixedSize(400, 400)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)  # Remove botão de fechar

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
            }
            QLabel {
                font-size: 16px;
                color: #333;
                padding: 10px;
                qproperty-alignment: AlignCenter;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton {
                background-color: white;
                color: #f7931e;
                font-weight: bold;
                border: 2px solid #f7931e;
                border-radius: 6px;
                padding: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #fef3e7;
            }
        """)

        layout = QVBoxLayout()
        label = QLabel(mensagem)
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setPlaceholderText("Digite a senha...")

        validar_btn = QPushButton("OK")
        validar_btn.clicked.connect(self.validar)

        layout.addWidget(label)
        layout.addWidget(self.senha_input)
        layout.addWidget(validar_btn)
        self.setLayout(layout)

        self.valido = False

    def validar(self):
        if self.senha_input.text() == "1234":
            self.valido = True
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", "Senha incorreta")

class ValidadorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validador de Pacotes")
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("""
            * { font-family: 'Roboto'; font-size: 14px; }
            QWidget { background-color: #f8f9fa; }
            QPushButton {
                background-color: #6200ee;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #3700b3;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                color: black;
            }
            QLabel {
                color: #212529;
            }
            QTableWidget {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                color: black;
            }
            QTableWidget::item {
                color: black;
                text-align: center;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                color: black;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.init_ui()

    def aplicar_sombra(self, widget):
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        widget.setGraphicsEffect(sombra)

    def init_ui(self):
        header = QLabel("Validador de Pacotes")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(header)

        self.status_label = QLabel("Aguardando PUG...")
        self.status_label.setStyleSheet("color: #495057;")

        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("Bipar código...")
        self.entrada.returnPressed.connect(self.processar_codigo)

        self.contador_label = QLabel("Pacotes válidos: 0")
        self.contador_label.setStyleSheet("font-weight: bold; margin: 5px 0;")

        self.reset_btn = QPushButton("Resetar")
        self.reset_btn.setIcon(QIcon("reset_icon.svg"))
        self.reset_btn.setIconSize(QSize(16, 16))
        self.reset_btn.clicked.connect(self.resetar)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.entrada, 3)
        header_layout.addWidget(self.reset_btn, 1)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["N", "PUG", "Código de Rastreio", "Etiqueta"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.aplicar_sombra(self.table)

        self.table_pugs = QTableWidget(0, 2)
        self.table_pugs.setHorizontalHeaderLabels(["PUG", "Qtd Pacotes"])
        self.table_pugs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_pugs.setMaximumHeight(140)
        self.aplicar_sombra(self.table_pugs)

        # Remover a coluna de números (índices) à esquerda
        self.table.verticalHeader().setVisible(False)

        self.main_layout.addLayout(header_layout)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.contador_label)
        self.main_layout.addWidget(self.table)
        self.main_layout.addWidget(QLabel("Resumo por PUG"))
        self.main_layout.addWidget(self.table_pugs)

    def processar_codigo(self):
        global ultimo_codigo, contador_validos, pug_atual, estado

        codigo = self.entrada.text().strip()
        self.entrada.clear()
        if not codigo:
            return

        if estado == "aguardando_pug":
            if regex_pug.match(codigo):
                if codigo in pug_contagem:
                    self.status_label.setText("⚠️ Esse PUG já foi usado.")
                else:
                    pug_atual = codigo
                    contador_validos = 0
                    ordem_por_pug[pug_atual] = 0
                    self.contador_label.setText(f"Pacotes válidos: {contador_validos}")
                    self.status_label.setText("✅ PUG registrado. Bipar código de rastreio (PNL).")
                    estado = "aguardando_rastreio"
            else:
                self.status_label.setText("❌ PUG inválido. Formato incorreto.")
            return

        if estado == "aguardando_rastreio":
            if not codigo.startswith("PNL"):
                self.status_label.setText("❌ Código de rastreio deve começar com PNL.")
            elif codigo in pacotes_bipados:
                self.marcar_duplicado(codigo)
                pacote_duplicado = self.obter_info_pacote(codigo)  # Obter informações do pacote duplicado
                mensagem = (f"Erro de duplicado:\n"
                    f"N: {pacote_duplicado['N']}\n"
                    f"PUG: {pacote_duplicado['PUG']}\n"
                    f"Rastreio: {pacote_duplicado['Rastreio']}\n"
                    f"Etiqueta: {pacote_duplicado['Etiqueta']}")
                if not self.pedir_senha(mensagem):
                    return
                self.limpar_duplicado(codigo)
            else:
                ultimo_codigo = {"rastreio": codigo, "etiqueta": None}
                self.status_label.setText("🔄 Código de rastreio lido. Bipar etiqueta.")
                estado = "aguardando_etiqueta"
            return

        if estado == "aguardando_etiqueta":
            rastreio = ultimo_codigo["rastreio"]
            etiqueta = codigo
            resultado = df[df["[Codigo de Rastreio]"] == rastreio]
            if resultado.empty or resultado["[Etiqueta Last Mile]"].values[0] != etiqueta:
                if not self.pedir_senha("Etiqueta não corresponde ao código de rastreio."):
                    return
                self.status_label.setText("🔄 Bipar código de rastreio.")
                estado = "aguardando_rastreio"
                return

            if rastreio in pacotes_bipados:
                self.marcar_duplicado(rastreio)
                if not self.pedir_senha("Código de rastreio duplicado detectado!"):
                    return
                self.limpar_duplicado(rastreio)

            self.adicionar_tabela(pug_atual, rastreio, etiqueta)
            pacotes_bipados.add(rastreio)
            contador_validos += 1
            self.contador_label.setText(f"Pacotes válidos: {contador_validos}")
            self.status_label.setText("✅ Pacote registrado com sucesso!")
            self.atualizar_pug(pug_atual)
            estado = "aguardando_rastreio"

    def adicionar_tabela(self, pug, rastreio, etiqueta):
        if pug not in ordem_por_pug:
            ordem_por_pug[pug] = 1
        else:
            ordem_por_pug[pug] += 1
        ordem = ordem_por_pug[pug]
        row = self.table.rowCount()
        self.table.insertRow(row)
        for i, valor in enumerate([ordem, pug, rastreio, etiqueta]):
            item = QTableWidgetItem(str(valor))
            item.setForeground(QColor("black"))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, i, item)
        linhas_destacadas[rastreio] = row

    def atualizar_pug(self, pug):
        if pug in pug_contagem:
            pug_contagem[pug] += 1
        else:
            pug_contagem[pug] = 1
        for row in range(self.table_pugs.rowCount()):
            if self.table_pugs.item(row, 0).text() == pug:
                self.table_pugs.setItem(row, 1, QTableWidgetItem(str(pug_contagem[pug])))
                return
        row = self.table_pugs.rowCount()
        self.table_pugs.insertRow(row)
        self.table_pugs.setItem(row, 0, QTableWidgetItem(pug))
        self.table_pugs.setItem(row, 1, QTableWidgetItem(str(pug_contagem[pug])))

    def marcar_duplicado(self, rastreio):
        if rastreio in linhas_destacadas:
            row = linhas_destacadas[rastreio]
            for col in range(self.table.columnCount()):
                self.table.item(row, col).setBackground(QColor("red"))

    def limpar_duplicado(self, rastreio):
        if rastreio in linhas_destacadas:
            row = linhas_destacadas[rastreio]
            for col in range(self.table.columnCount()):
                self.table.item(row, col).setBackground(QColor("white"))
    
    def obter_info_pacote(self, rastreio):
        # Procurar a linha correspondente ao rastreio
        for row in range(self.table.rowCount()):
            if self.table.item(row, 2).text() == rastreio:  # Coluna 2 é o código de rastreio
                n = self.table.item(row, 0).text()  # Coluna 0 é o número da linha
                pug = self.table.item(row, 1).text()  # Coluna 1 é o PUG
                etiqueta = self.table.item(row, 3).text()  # Coluna 3 é a etiqueta
                return {"N": n, "PUG": pug, "Rastreio": rastreio, "Etiqueta": etiqueta}
        return {}

    def pedir_senha(self, mensagem):
        dialog = SenhaDialog(mensagem)
        return dialog.exec() == QDialog.Accepted

    def resetar(self):
        global ultimo_codigo, pug_atual, estado, contador_validos
        ultimo_codigo = None
        pug_atual = None
        estado = "aguardando_pug"
        contador_validos = 0
        self.contador_label.setText("Pacotes válidos: 0")
        self.status_label.setText("🔁 Reiniciado. Aguardando novo PUG...")
        self.entrada.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ValidadorApp()
    window.show()
    sys.exit(app.exec())
