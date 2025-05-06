import pandas as pd
import requests
from io import StringIO
import os
import sys
import logging
from dotenv import load_dotenv


# Detecta se está rodando como .exe (PyInstaller)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

dotenv_path = os.path.join(base_path, ".env")

def carregar_csv_github():
    load_dotenv()  # Carrega variáveis do .env

    url = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/refs/heads/main/App_Conferencia/Db_Pacotes_Enjoei.csv"
    token = os.getenv("GITHUB_TOKEN")

    headers = {"Authorization": f"token {token}"} if token else {}
    
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            logging.info("CSV carregado com sucesso do GitHub.")
            return pd.read_csv(StringIO(response.text))
        else:
            logging.error(f"Erro {response.status_code} ao acessar CSV no GitHub.")
            raise Exception(f"Erro {response.status_code} ao acessar CSV")
    except Exception as e:
        logging.exception(f"Falha ao carregar CSV do GitHub: {e}")
        raise