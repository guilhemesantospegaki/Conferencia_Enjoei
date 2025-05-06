import pandas as pd
import requests
from io import StringIO
import os
from dotenv import load_dotenv


def carregar_csv_github():
    load_dotenv()  # Carrega variáveis do .env

    url = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/refs/heads/main/App_Conferencia/Db_Pacotes_Enjoei.csv"
    token = os.getenv("GITHUB_TOKEN")

    headers = {"Authorization": f"token {token}"} if token else {}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        raise Exception(f"Erro {response.status_code} ao acessar CSV")