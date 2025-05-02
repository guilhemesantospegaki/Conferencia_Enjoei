import requests
import os
import sys
import shutil
import logging

# Configura log em arquivo
logging.basicConfig(
    filename="atualizador.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Versão atual do app
VERSAO_ATUAL = "1.0.3"

# Link para a versão mais recente
URL_VERSAO = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/refs/heads/main/App_Conferencia/versao.txt"

# Link direto para o executável da última versão (atenção ao nome com espaço e acento)
URL_EXE = "https://github.com/guilhemesantospegaki/Conferencia_Enjoei/releases/download/v1.0.3/Conferencia.Enjoei.exe"

def verificar_e_atualizar():
    try:
        logging.info("Verificando nova versão...")
        versao_online = requests.get(URL_VERSAO, timeout=5).text.strip()
        logging.info(f"Versão online: {versao_online} | Versão atual: {VERSAO_ATUAL}")

        if versao_online != VERSAO_ATUAL:
            logging.info("Nova versão detectada, iniciando atualização.")
            baixar_e_substituir()
        else:
            logging.info("Aplicativo já está na versão mais recente.")
    except Exception as e:
        logging.error(f"Erro ao verificar atualização: {e}")

def baixar_e_substituir():
    try:
        logging.info("Baixando nova versão...")
        response = requests.get(URL_EXE, stream=True)
        with open("Conferência Enjoei_novo.exe", "wb") as f:
            shutil.copyfileobj(response.raw, f)

        logging.info("Substituindo executável antigo...")
        os.rename("Conferência Enjoei.exe", "Conferência Enjoei_backup.exe")
        os.rename("Conferência Enjoei_novo.exe", "Conferência Enjoei.exe")

        logging.info("Reiniciando aplicativo atualizado...")
        os.startfile("Conferência Enjoei.exe")
        sys.exit()
    except Exception as e:
        logging.error(f"Erro durante atualização: {e}")
