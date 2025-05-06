from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                                 QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, 
                                 QFrame, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy, QFileDialog)
from PySide6.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
from PySide6.QtCore import Qt, QSize, QTimer, QDateTime
from datetime import datetime
from core.github_csv import carregar_csv_github
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
import pandas as pd
import re
import logging
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO")

# Cria o log no mesmo diretório onde o script está sendo executado
logging.basicConfig(
    filename=os.path.join(os.getcwd(), "conferencia_erros.log"),
    level=logging.ERROR,  # Ou INFO se quiser registrar também os eventos não críticos
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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
df = carregar_csv_github()

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 220)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Container com bordas arredondadas e sombra
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: #331C72;
                border-radius: 20px;
            }
        """)
        self.container.setGeometry(0, 0, 400, 220)

        # Efeito de sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.container.setGraphicsEffect(shadow)

        # Layout do conteúdo
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        # Título
        self.title = QLabel("Conferência Enjoei")
        self.title.setFont(QFont("Roboto", 20, QFont.Bold))
        self.title.setStyleSheet("color: white;")
        self.title.setAlignment(Qt.AlignCenter)

        # Logo
        self.logo = QLabel()
        pixmap = QPixmap("assets/Mono Pegaki_Fundo escuro.png")
        pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(Qt.AlignCenter)

        # Adiciona os elementos ao layout
        layout.addWidget(self.title)
        layout.addWidget(self.logo)

    def start(self, main_window_cls):
        QTimer.singleShot(3000, lambda: self.open_main_window(main_window_cls))

    def open_main_window(self, main_window_cls):
        self.main = main_window_cls()
        self.main.show()
        self.close()

class SenhaDialog(QDialog):
    def __init__(self, mensagem="Acesso restrito.\nDigite a senha para continuar."):
        super().__init__()
        self.setWindowTitle("Autenticação")
        self.setFixedSize(320, 240)

        # Janela sem borda
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint)

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Mensagem
        self.label = QLabel(mensagem)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 15px; color: #333;")
        layout.addWidget(self.label)

        # Campo de senha
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setPlaceholderText("Digite a senha")
        self.senha_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: white;
                color: black;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.senha_input)

        # Botão OK
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.validar)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #331C72;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3700b3;
            }
        """)
        layout.addWidget(self.ok_btn)

        # Estilo da caixa de diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                border-radius: 20px
            }
        """)
    def closeEvent(self, event):
        # Impede o fechamento da janela sem a senha
        event.ignore()  # Ignora a tentativa de fechar a janela
        self.show()  # Mostra novamente a janela, garantindo que não será fechada sem senha

    def validar(self):
        if self.senha_input.text() == "XD@2025":
            self.accept()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Acesso Negado")
            msg.setText("A senha está incorreta.\n\nPor favor, tente novamente ou contate um supervisor.")
            
            # Modificar o estilo da mensagem
            msg.setIcon(QMessageBox.Critical)
            
            # Personalizando o botão
            msg.setStandardButtons(QMessageBox.Ok)
            ok_button = msg.button(QMessageBox.Ok)
            ok_button.setStyleSheet("background-color: #ff4d4d; color: white; font-weight: bold;")
            
            # Personalizar a fonte
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #f2f2f2;
                    border-radius: 10px;
                    font-family: 'Roboto', sans-serif;
                    font-size: 14px;
                }
                QMessageBox QLabel {
                    color: #333;
                }
            """)
            
            # Exibe a mensagem de erro
            msg.exec_()

class ValidadorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conferência Enjoei")
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

        # Layout principal dividido em 2: Cabeçalho à esquerda e conteúdo à direita
        self.main_layout = QHBoxLayout(self)

        # Cabeçalho com o logo à esquerda
        self.logo_frame = QFrame()
        self.logo_layout = QVBoxLayout(self.logo_frame)

        # Carrega e redimensiona o logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/Pegaki_Fundo branco.png")  # Caminho da imagem
        scaled_pixmap = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # Adiciona o logo e o spacer
        self.logo_layout.addWidget(logo_label)

        # Linha separadora entre "Validação" e "Log de Erro"
        self.line_validacao = QFrame()
        self.line_validacao.setFrameShape(QFrame.HLine)
        self.line_validacao.setStyleSheet("background-color: #ced4da;")

        # Adiciona a linha separadora
        self.logo_layout.addWidget(self.line_validacao)

        # Adiciona o botão "Validação"
        self.btn_validacao = QPushButton("Validação")
        self.btn_validacao.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #092B1C;
                font-family: 'Roboto', sans-serif;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                color: #3700b3;
            }
        """)
        self.btn_validacao.setIcon(QIcon("validacao_icon.svg"))
        self.btn_validacao.setIconSize(QSize(16, 16))
        self.logo_layout.addWidget(self.btn_validacao)
        # Conectar o botão ao método para mostrar a tela de erros
        self.btn_validacao.clicked.connect(self.mostrar_validacao)

        # Adiciona o botão "Log de Erro"
        self.btn_log_erro = QPushButton("Log de Erro")
        self.btn_log_erro.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #092B1C;
                font-family: 'Roboto', sans-serif;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                color: #3700b3;
            }
        """)
        self.btn_log_erro.setIcon(QIcon("log_icon.svg"))
        self.btn_log_erro.setIconSize(QSize(16, 16))
        self.logo_layout.addWidget(self.btn_log_erro)
        # Conectar o botão ao método para mostrar a tela de erros
        self.btn_log_erro.clicked.connect(self.mostrar_erros_somente_com_senha)

        spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.logo_layout.addItem(spacer_item)

        # Adiciona o cabeçalho com a proporção de 1/5 da tela (ou o valor que você desejar)
        self.main_layout.addWidget(self.logo_frame)

        # Linha separadora entre o cabeçalho e o conteúdo
        self.line_frame = QFrame()
        self.line_frame.setFrameShape(QFrame.VLine)
        self.line_frame.setFrameShadow(QFrame.Sunken)
        self.line_frame.setStyleSheet("background-color: #ced4da; border: none;")  # Linha suave

        # Adiciona a linha separadora entre cabeçalho e conteúdo
        self.main_layout.addWidget(self.line_frame)

        # Layout principal para o conteúdo da aplicação à direita
        self.content_frame = QWidget()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.main_layout.addWidget(self.content_frame)

        # Definir a proporção do cabeçalho e do conteúdo
        self.main_layout.setStretch(0, 1)  # Cabeçalho ocupa 1 parte
        self.main_layout.setStretch(1, 0)  # Linha separadora ocupa 1 parte (visualmente pequena)
        self.main_layout.setStretch(2, 4)  # Conteúdo ocupa 4 partes

        self.stack_layout = QVBoxLayout()  # Simples substituto para um stack, você pode usar QStackedLayout se preferir
        self.validacao_widget = QWidget()
        self.erros_widget = QWidget()

        self.stack_layout.addWidget(self.validacao_widget)
        self.stack_layout.addWidget(self.erros_widget)
        self.content_layout.addLayout(self.stack_layout)

        self.erros = []  # Inicializar lista de erros aqui

        self.init_validacao_ui()
        self.init_erros_ui()

        self.mostrar_validacao()

    def closeEvent(self, event):
        try:
            self.exportar_tabela_para_excel(self.table)
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
        event.accept()
    
    def exportar_tabela_para_excel(self, table_widget):
        # Pega os dados da QTableWidget
        colunas = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]
        dados = []

        for row in range(table_widget.rowCount()):
            linha = []
            for col in range(table_widget.columnCount()):
                item = table_widget.item(row, col)
                linha.append(item.text() if item else "")
            dados.append(linha)

        # Cria um DataFrame com os dados
        df = pd.DataFrame(dados, columns=colunas)

        # Abre janela para salvar arquivo
        caminho_arquivo, _ = QFileDialog.getSaveFileName(
            None,
            "Salvar como Excel",
            "Pacotes Validados.xlsx",
            "Arquivos Excel (*.xlsx)"
        )

        if caminho_arquivo:
            df.to_excel(caminho_arquivo, index=False)
            print(f"Arquivo salvo com sucesso em: {caminho_arquivo}")

    def exportar_log_de_erros(self, table_widget):
       # Pega os dados da QTableWidget
        colunas = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]
        dados = []

        for row in range(table_widget.rowCount()):
            linha = []
            for col in range(table_widget.columnCount()):
                item = table_widget.item(row, col)
                linha.append(item.text() if item else "")
            dados.append(linha)

        # Cria um DataFrame com os dados
        df = pd.DataFrame(dados, columns=colunas)

        # Abre janela para salvar arquivo
        caminho_arquivo, _ = QFileDialog.getSaveFileName(
            None,
            "Salvar como Excel",
            "Log de Erros.xlsx",
            "Arquivos Excel (*.xlsx)"
        )

        if caminho_arquivo:
            df.to_excel(caminho_arquivo, index=False)
            print(f"Arquivo salvo com sucesso em: {caminho_arquivo}")

    def aplicar_sombra(self, widget):
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        widget.setGraphicsEffect(sombra)

    def init_validacao_ui(self):
        self.validacao_layout = QVBoxLayout(self.validacao_widget)
        self.stack_layout.addWidget(self.validacao_widget)

        header = QLabel("Validador de Pacotes")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        self.validacao_layout.addWidget(header)

        self.status_label = QLabel("Aguardando PUG...")
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("Bipar código...")
        self.entrada.returnPressed.connect(self.processar_codigo)

        self.contador_label = QLabel("Pacotes válidos: 0")

        self.reset_btn = QPushButton("Resetar")
        self.reset_btn.setIcon(QIcon("reset_icon.svg"))
        self.reset_btn.setIconSize(QSize(16, 16))
        self.reset_btn.clicked.connect(self.ao_clicar_resetar)

        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #331C72;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-family: 'Roboto';
            }
            QPushButton:hover {
                background-color: #4b2fa2;
            }
            QPushButton:pressed {
                background-color: #260f5c;
            }
        """)

        entrada_layout = QHBoxLayout()
        entrada_layout.addWidget(self.entrada, 3)
        entrada_layout.addWidget(self.reset_btn, 1)

        self.validacao_layout.addLayout(entrada_layout)
        self.validacao_layout.addWidget(self.status_label)
        self.validacao_layout.addWidget(self.contador_label)

        # Tabela principal
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["N", "PUG", "Código de Rastreio", "Etiqueta"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Remover a coluna de índice da tabela principal
        self.table.verticalHeader().setVisible(False)

        # Tabela de PUGs
        self.table_pugs = QTableWidget(0, 2)
        self.table_pugs.setHorizontalHeaderLabels(["PUG", "Qtd Pacotes"])
        self.table_pugs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_pugs.setMaximumHeight(140)

        # Remover a coluna de índice da tabela de PUGs
        self.table_pugs.verticalHeader().setVisible(False)

        self.validacao_layout.addWidget(self.status_label)
        self.validacao_layout.addWidget(self.contador_label)
        self.validacao_layout.addWidget(self.table)
        self.validacao_layout.addWidget(QLabel("Resumo por PUG"))
        self.validacao_layout.addWidget(self.table_pugs)

    def init_erros_ui(self):
        self.erros_layout = QVBoxLayout(self.erros_widget)
        self.stack_layout.addWidget(self.erros_widget)

        titulo = QLabel("Erros Registrados")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px 0;")
        self.erros_layout.addWidget(titulo)

        # Botão de download com ícone
        download_button = QPushButton()
        download_button.setIcon(QIcon("download_icon.svg"))  # Defina o caminho do ícone desejado
        download_button.setIconSize(QSize(30, 30))  # Ajuste o tamanho do ícone
        download_button.setStyleSheet("""
                                        QPushButton {
                                            background-color: transparent;
                                            border: none;
                                        }
                                        QPushButton:hover {
                                            background-color: rgba(0, 0, 0, 0.05); /* opcional: um leve hover */
                                            border-radius: 5px;
                                        }
                                    """)
        download_button.setToolTip("Baixar Erros em Excel")
        download_button.clicked.connect(lambda: self.exportar_log_de_erros(self.erros_table))
        self.erros_layout.addWidget(download_button, alignment=Qt.AlignRight)  # Ajuste o alinhamento do botão (direita neste caso)

        self.erros_table = QTableWidget(0, 5)
        self.erros_table.setHorizontalHeaderLabels(["Data/Hora", "Tipo de Erro", "PUG", "Rastreio", "Etiqueta"])
        self.erros_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.erros_layout.addWidget(self.erros_table)

    def mostrar_validacao(self):
        self.validacao_widget.show()
        self.erros_widget.hide()

    def mostrar_erros_somente_com_senha(self):
        if self.pedir_senha("Digite a senha para acessar os erros."):
            self.mostrar_erros()

    def mostrar_erros(self):
        self.validacao_widget.hide()
        self.erros_widget.show()

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
                    logging.error(f"PUG duplicado detectado: {codigo}")
                else:
                    pug_atual = codigo
                    contador_validos = 0
                    ordem_por_pug[pug_atual] = 0
                    self.contador_label.setText(f"Pacotes válidos: {contador_validos}")
                    self.status_label.setText("✅ PUG registrado. Bipar código de rastreio (PNL).")
                    estado = "aguardando_rastreio"
            else:
                self.status_label.setText("❌ PUG inválido. Formato incorreto.")
                logging.error(f"PUG inválido: {codigo}")
            return

        if estado == "aguardando_rastreio":
            if not codigo.startswith("PNL"):
                self.status_label.setText("❌ Código de rastreio deve começar com PNL.")
                logging.error(f"Rastreio inválido (não começa com PNL): {codigo}")
            elif codigo in pacotes_bipados:
                self.status_label.setText("❌ Código de rastreio duplicado detectado! ❌")
                self.marcar_duplicado(codigo)
                pacote_duplicado = self.obter_info_pacote(codigo)  # Obter informações do pacote duplicado
                self.salvar_erro("Duplicado", pug_atual, codigo, pacote_duplicado['Etiqueta'])
                mensagem = (f"<b>Erro: Pacotes Duplicados</b><br>"
                    f"Pacote: {pacote_duplicado['N']}<br>"
                    f"{pacote_duplicado['PUG']}<br>"
                    f"Código: {pacote_duplicado['Rastreio']}<br>"
                    f"Etiqueta: {pacote_duplicado['Etiqueta']}")
                logging.error(f"Pacote duplicado detectado: {codigo} - PUG: {pug_atual}")
                if not self.pedir_senha(mensagem):
                    return
                self.limpar_duplicado(codigo)
                self.status_label.setText("🔄 Bipar código de rastreio.")
            else:
                ultimo_codigo = {"rastreio": codigo, "etiqueta": None}
                self.status_label.setText("🔄 Código de rastreio lido. Bipar etiqueta.")
                estado = "aguardando_etiqueta"
            return

        if estado == "aguardando_etiqueta":
            rastreio = ultimo_codigo["rastreio"]
            etiqueta = codigo
            resultado = df[df["[Codigo de Rastreio]"] == rastreio]
            
            if resultado.empty:
                self.status_label.setText("❌ Código de rastreio não encontrado na base. ❌")
                logging.error(f"Código de rastreio não encontrado na base: {rastreio}")
                self.salvar_erro("Inconsistência", pug_atual, rastreio, etiqueta)
                if not self.pedir_senha("Código de rastreio não encontrado na base."):
                    return
                self.status_label.setText("🔄 Bipar código de rastreio.")
                estado = "aguardando_rastreio"
                return
            
            # Obtenção da etiqueta da base de dados
            etiqueta_base = resultado["[Etiqueta Last Mile]"].values[0]

            if etiqueta_base != etiqueta:
                self.status_label.setText("❌ Etiqueta não corresponde ao código de rastreio. ❌")
                logging.error(f"Etiqueta não corresponde ao código de rastreio. "
                  f"Rastreio: {rastreio}, Etiqueta na base: {etiqueta_base}, Etiqueta bipada: {etiqueta}")
                self.salvar_erro("Inconsistência", pug_atual, rastreio, etiqueta)
                if not self.pedir_senha("Etiqueta não corresponde ao código de rastreio."):
                    return
                self.status_label.setText("🔄 Bipar código de rastreio.")
                estado = "aguardando_rastreio"
                return

            if rastreio in pacotes_bipados:
                self.marcar_duplicado(rastreio)
                logging.error(f"Rastreio duplicado detectado: {rastreio}")
                if not self.pedir_senha("Código de rastreio duplicado detectado!"):
                    return
                self.status_label.setText("🔄 Bipar código de rastreio.")
                self.limpar_duplicado(rastreio)
                estado = "aguardando_rastreio"
                return

            self.adicionar_tabela(pug_atual, rastreio, etiqueta)
            pacotes_bipados.add(rastreio)
            contador_validos += 1
            self.contador_label.setText(f"Pacotes válidos: {contador_validos}")
            self.status_label.setText("✅ Pacote registrado com sucesso!")
            self.atualizar_pug(pug_atual)
            estado = "aguardando_rastreio"

    def salvar_erro(self, tipo, pug, rastreio, etiqueta):

        # Obtém a data e hora atual
        data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Adiciona uma nova linha na tabela de erros
        row = self.erros_table.rowCount()  # Obtem o número da próxima linha disponível
        self.erros_table.insertRow(row)  # Insere a nova linha na tabela de erros

        # Adiciona as colunas para o tipo de erro, PUG, rastreio e etiqueta
        for i, valor in enumerate([data_hora_atual, tipo, pug, rastreio, etiqueta]):
            item = QTableWidgetItem(str(valor))  # Cria um item para a célula
            item.setForeground(QColor("black"))  # Define a cor do texto
            item.setTextAlignment(Qt.AlignCenter)  # Alinha o texto no centro
            self.erros_table.setItem(row, i, item)  # Define o item na célula

    def adicionar_tabela(self, pug, rastreio, etiqueta):
        if pug not in ordem_por_pug:
            ordem_por_pug[pug] = 1
        else:
            ordem_por_pug[pug] += 1
        ordem = ordem_por_pug[pug]

        # Verifica se o PUG foi alterado e insere uma linha vazia se necessário
        if hasattr(self, 'ultimo_pug') and self.ultimo_pug != pug:
            self.table.insertRow(self.table.rowCount())  # Linha vazia
        self.ultimo_pug = pug  # Atualiza o último PUG

        row = self.table.rowCount()
        self.table.insertRow(row)
        for i, valor in enumerate([ordem, pug, rastreio, etiqueta]):
            item = QTableWidgetItem(str(valor))
            item.setForeground(QColor("black"))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, i, item)
        linhas_destacadas[rastreio] = row

        # >>> Adiciona no CSV automaticamente <<<
        caminho_csv = "validados.csv"
        caminho_csv_pug = f"{pug_atual}.csv"
        escrever_cabecalho = not os.path.exists(caminho_csv)

        for caminho_csv in [caminho_csv, caminho_csv_pug]:
            escrever_cabecalho = not os.path.exists(caminho_csv)
            with open(caminho_csv, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if escrever_cabecalho:
                    writer.writerow(["Ordem", "PUG", "Código de Rastreio", "Etiqueta"])
                writer.writerow([ordem, pug, rastreio, etiqueta])

    def atualizar_pug(self, pug):
        if pug in pug_contagem:
            pug_contagem[pug] += 1
        else:
            pug_contagem[pug] = 1
        for row in range(self.table_pugs.rowCount()):
            if self.table_pugs.item(row, 0).text() == pug:
                self.table_pugs.setItem(row, 1, QTableWidgetItem(str(pug_contagem[pug])))
                item = self.table_pugs.item(row, 1)
                item.setTextAlignment(Qt.AlignCenter)  # Alinha o texto ao centro             
                return
        row = self.table_pugs.rowCount()
        self.table_pugs.insertRow(row)
        pug_item = QTableWidgetItem(pug)
        contagem_item = QTableWidgetItem(str(pug_contagem[pug]))

        # Centralizar os itens
        pug_item.setTextAlignment(Qt.AlignCenter)
        contagem_item.setTextAlignment(Qt.AlignCenter)

        self.table_pugs.setItem(row, 0, pug_item)
        self.table_pugs.setItem(row, 1, contagem_item)

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


    def enviar_email_ao_fechar(self):

        # Caminho do arquivo a ser anexado (exemplo: "relatorio.csv" na raiz)
        arquivos_anexar = [f"{pug_atual}.csv", "conferencia_erros.log"]  # troque para o nome do seu arquivo

        # Cria o e-mail com texto e anexo
        msg = MIMEMultipart()
        msg['Subject'] = "Relatório App Conferência Enjoei"
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = EMAIL_DESTINATARIO

        # Corpo do e-mail
        corpo = MIMEText("Segue em anexo os eventos do aplicativo no dia.", "plain")
        msg.attach(corpo)

        for caminho_anexo in arquivos_anexar:
            with open(caminho_anexo, "rb") as arquivo:
                parte = MIMEBase("application", "octet-stream")
                parte.set_payload(arquivo.read())
                encoders.encode_base64(parte)
                parte.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(caminho_anexo)}"'
                )
                msg.attach(parte)

        # Envio
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.send_message(msg)


    def ao_clicar_resetar(self):
        self.enviar_email_ao_fechar()
        self.apagar_arquivos()
        self.resetar()

    def apagar_arquivos(self):
        arquivos = [f"{pug_atual}.csv", "conferencia_erros.log"]  # Substitua pelos nomes reais

        # Fecha handlers de logging se estiverem abertos
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()
                logger.removeHandler(handler)

        for arquivo in arquivos:
            if os.path.exists(arquivo):
                try:
                    os.remove(arquivo)
                    print(f"Arquivo '{arquivo}' apagado com sucesso.")
                except Exception as e:
                    print(f"Erro ao apagar '{arquivo}': {e}")
            else:
                print(f"Arquivo '{arquivo}' não encontrado.")
