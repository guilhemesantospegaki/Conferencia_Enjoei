import requests
import os
import sys
import shutil

# Versão atual do seu app
VERSAO_ATUAL = "1.0.0"

# Link cru para o versao.txt (ajuste com seu repositório real)
URL_VERSAO = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/main/versao.txt"

# Link direto para o .exe da nova versão
URL_EXE = "https://github.com/guilhemesantospegaki/Conferencia_Enjoei/releases/latest/download/Conferencia_Enjoei.exe"

def verificar_e_atualizar():
    try:
        versao_online = requests.get(URL_VERSAO, timeout=5).text.strip()
        if versao_online != VERSAO_ATUAL:
            print(f"Atualização disponível: {versao_online}")
            baixar_e_substituir()
    except Exception as e:
        print("Erro ao verificar atualização:", e)

def baixar_e_substituir():
    try:
        print("Baixando nova versão...")
        response = requests.get(URL_EXE, stream=True)
        with open("Conferencia_Enjoei_novo.exe", "wb") as f:
            shutil.copyfileobj(response.raw, f)

        print("Atualizando...")
        os.rename("Conferencia_Enjoei.exe", "Conferencia_Enjoei_antigo.exe")
        os.rename("Conferencia_Enjoei_novo.exe", "Conferencia_Enjoei.exe")

        print("Reiniciando nova versão...")
        os.startfile("Conferencia_Enjoei.exe")
        sys.exit()
    except Exception as e:
        print("Erro ao atualizar:", e)
