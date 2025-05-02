import requests
import os
import sys
import shutil
import logging

# Versão atual do app - você deve alterar isso em cada release
VERSAO_ATUAL = "1.0.1"

# Link para o versao.txt no GitHub
URL_VERSAO = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/main/versao.txt"

# Link direto para o .exe da última release (você sobe isso em Releases)
URL_EXE = "https://github.com/guilhemesantospegaki/Conferencia_Enjoei/releases/download/v1.0.1/Conferencia.Enjoei.exe"

# Configuração de logs
logging.basicConfig(filename='atualizacao.log', level=logging.INFO, format='%(asctime)s - %(message)s')

NOME_EXECUTAVEL = "Conferência Enjoei.exe"

def verificar_e_atualizar():
    try:
        versao_online = requests.get(URL_VERSAO, timeout=5).text.strip()
        if versao_online != VERSAO_ATUAL:
            logging.info(f"Nova versão disponível: {versao_online}")
            print(f"Nova versão disponível: {versao_online}")
            baixar_e_substituir()
        else:
            logging.info("Aplicativo está na versão mais recente.")
            print("Aplicativo está na versão mais recente.")
    except Exception as e:
        logging.error("Erro ao verificar atualização: " + str(e))
        print("Erro ao verificar atualização:", e)

def baixar_e_substituir():
    try:
        logging.info("Baixando nova versão...")
        print("Baixando nova versão...")
        response = requests.get(URL_EXE, stream=True)
        with open("Conferência Enjoei_novo.exe", "wb") as f:
            shutil.copyfileobj(response.raw, f)

        logging.info("Substituindo executável antigo...")
        print("Substituindo executável antigo...")
        os.rename(NOME_EXECUTAVEL, "Conferência Enjoei_backup.exe")
        os.rename("Conferência Enjoei_novo.exe", NOME_EXECUTAVEL)

        logging.info("Reiniciando app com nova versão...")
        print("Reiniciando app com nova versão...")
        os.startfile(NOME_EXECUTAVEL)
        sys.exit()
    except Exception as e:
        logging.error("Erro ao atualizar: " + str(e))
        print("Erro ao atualizar:", e)


